from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .base import FunctionalityResult
from .profiles import CRITERIA, GAME_PROFILES, GameProfile, StaticCheck, TestPort


RUNTIME_KEYS = {
    "state_changed",
    "input_effective",
    "feedback_visible",
    "terminated",
}

CRITERION_RUNTIME_KEYS = {
    "rule_completeness": ("state_changed", "feedback_visible"),
    "state_evolution": ("state_changed",),
    "interaction_validity": ("input_effective",),
    "goal_feedback_alignment": ("feedback_visible",),
    "constraint_termination": ("terminated",),
}


def evaluate_profiled_functionality(
    game_id: str,
    code_path: Path | str,
    runtime_signals: dict[str, Any] | None = None,
    source_code: str | None = None,
) -> FunctionalityResult | None:
    profile = GAME_PROFILES.get(game_id)
    if profile is None:
        return None

    source = source_code if source_code is not None else Path(code_path).read_text(encoding="utf-8", errors="ignore")
    runtime = _normalize_runtime_signals(runtime_signals)
    port_results = {
        port.port_id: _evaluate_port(port, source, runtime)
        for port in profile.test_ports
    }

    criteria_scores: dict[str, int] = {}
    reasons: dict[str, str] = {}
    criteria_evidence: dict[str, Any] = {}
    review_required: list[str] = []

    for criterion in CRITERIA:
        score, reason, evidence = _score_criterion(criterion, profile, port_results, runtime)
        criteria_scores[criterion] = score
        reasons[criterion] = reason
        criteria_evidence[criterion] = evidence
        if evidence.get("review_required"):
            review_required.append(criterion)

    return FunctionalityResult(
        passed=sum(criteria_scores.values()),
        total=10,
        criteria_scores=criteria_scores,
        reasons=reasons,
        evidence={
            "profile": {
                "game_id": profile.game_id,
                "display_name": profile.display_name,
                "test_port_count": len(profile.test_ports),
            },
            "runtime_signals": runtime,
            "criteria": criteria_evidence,
            "review_required": review_required,
            "method": "profiled_test_ports_static_first_runtime_assisted",
        },
        specialized_items=port_results,
    )


def _normalize_runtime_signals(runtime_signals: dict[str, Any] | None) -> dict[str, Any]:
    normalized: dict[str, Any] = {key: False for key in RUNTIME_KEYS}
    normalized["__provided__"] = runtime_signals is not None
    normalized["test_ports"] = {}
    if runtime_signals is None:
        return normalized

    for key in RUNTIME_KEYS:
        if key in runtime_signals:
            normalized[key] = bool(runtime_signals[key])

    test_ports = runtime_signals.get("test_ports") or runtime_signals.get("ports") or {}
    if isinstance(test_ports, dict):
        normalized["test_ports"] = test_ports
    return normalized


def _evaluate_port(port: TestPort, source: str, runtime: dict[str, Any]) -> dict[str, Any]:
    static_checks = [_evaluate_static_check(check, source) for check in port.static_checks]
    passed_static_checks = sum(1 for check in static_checks if check["passed"])
    static_level = _static_level(passed_static_checks, len(static_checks))
    runtime_evidence = _evaluate_runtime_for_port(port, runtime)

    if runtime_evidence["level"] == "strong" and static_level != "none":
        status = "PASS"
    elif static_level == "strong" and runtime_evidence["level"] in {"medium", "strong"}:
        status = "PASS"
    elif static_level != "none" or runtime_evidence["level"] != "none":
        status = "PARTIAL"
    else:
        status = "FAIL"

    return {
        "id": port.port_id,
        "name": port.name,
        "target": port.target,
        "criteria": list(port.criteria),
        "status": status,
        "static_level": static_level,
        "static_checks": static_checks,
        "runtime_level": runtime_evidence["level"],
        "runtime_evidence": runtime_evidence,
    }


def _evaluate_static_check(check: StaticCheck, source: str) -> dict[str, Any]:
    if check.regex:
        matches = [
            pattern
            for pattern in check.patterns
            if re.search(pattern, source, flags=re.IGNORECASE | re.MULTILINE)
        ]
    else:
        lower_source = source.lower()
        matches = [
            pattern
            for pattern in check.patterns
            if pattern.lower() in lower_source
        ]

    if check.mode == "all":
        passed = len(matches) == len(check.patterns)
    else:
        passed = len(matches) > 0

    return {
        "name": check.name,
        "passed": passed,
        "matched": matches,
        "mode": check.mode,
    }


def _static_level(passed: int, total: int) -> str:
    if total == 0:
        return "none"
    if passed == total:
        return "strong"
    if passed >= max(1, total // 2):
        return "medium"
    if passed > 0:
        return "weak"
    return "none"


def _evaluate_runtime_for_port(port: TestPort, runtime: dict[str, Any]) -> dict[str, Any]:
    exact = _runtime_port_status(port.port_id, runtime.get("test_ports", {}))
    if exact is not None:
        return {
            "source": "test_port",
            "status": exact,
            "level": _runtime_status_level(exact),
            "required_keys": list(port.runtime_keys),
            "matched_keys": [],
        }

    matched = [key for key in port.runtime_keys if bool(runtime.get(key, False))]
    if port.runtime_keys and len(matched) == len(port.runtime_keys):
        level = "medium"
    elif matched:
        level = "weak"
    else:
        level = "none"

    return {
        "source": "generic_runtime",
        "status": "PARTIAL" if level != "none" else "FAIL",
        "level": level,
        "required_keys": list(port.runtime_keys),
        "matched_keys": matched,
    }


def _runtime_port_status(port_id: str, test_ports: dict[str, Any]) -> str | None:
    if port_id not in test_ports:
        return None
    raw = test_ports[port_id]
    if isinstance(raw, bool):
        return "PASS" if raw else "FAIL"
    if isinstance(raw, str):
        status = raw.strip().upper()
        return status if status in {"PASS", "PARTIAL", "FAIL"} else None
    if isinstance(raw, dict):
        status = str(raw.get("status", "")).strip().upper()
        if status in {"PASS", "PARTIAL", "FAIL"}:
            return status
        if "passed" in raw:
            return "PASS" if bool(raw["passed"]) else "FAIL"
    return None


def _runtime_status_level(status: str) -> str:
    if status == "PASS":
        return "strong"
    if status == "PARTIAL":
        return "medium"
    return "none"


def _score_criterion(
    criterion: str,
    profile: GameProfile,
    port_results: dict[str, dict[str, Any]],
    runtime: dict[str, Any],
) -> tuple[int, str, dict[str, Any]]:
    related_ports = [
        result
        for port in profile.test_ports
        if criterion in port.criteria
        for result in [port_results[port.port_id]]
    ]
    pass_ports = [item for item in related_ports if item["status"] == "PASS"]
    partial_ports = [item for item in related_ports if item["status"] == "PARTIAL"]
    fail_ports = [item for item in related_ports if item["status"] == "FAIL"]

    runtime_support = _criterion_runtime_support(criterion, related_ports, runtime)
    review_required = False
    cap_reason = ""

    if pass_ports:
        score = 2
        reason = f"{len(pass_ports)} test port(s) passed for {criterion}."
    elif partial_ports:
        score = 1
        reason = f"{len(partial_ports)} test port(s) partially support {criterion}."
    else:
        score = 0
        reason = f"No usable test-port evidence for {criterion}."

    if score == 2 and runtime.get("__provided__", False) and not runtime_support["supported"]:
        score = 1
        review_required = True
        cap_reason = "Static evidence is strong, but runtime did not support this criterion; capped at 1."
        reason = f"{reason} {cap_reason}"

    return score, reason, {
        "criterion": criterion,
        "score": score,
        "ports": [item["id"] for item in related_ports],
        "pass_ports": [item["id"] for item in pass_ports],
        "partial_ports": [item["id"] for item in partial_ports],
        "fail_ports": [item["id"] for item in fail_ports],
        "runtime_support": runtime_support,
        "review_required": review_required,
        "cap_reason": cap_reason,
    }


def _criterion_runtime_support(
    criterion: str,
    related_ports: list[dict[str, Any]],
    runtime: dict[str, Any],
) -> dict[str, Any]:
    exact_pass_ports = [
        item["id"]
        for item in related_ports
        if item["runtime_evidence"]["source"] == "test_port"
        and item["runtime_evidence"]["status"] == "PASS"
    ]
    if exact_pass_ports:
        return {
            "supported": True,
            "source": "test_port",
            "matched_ports": exact_pass_ports,
            "required_keys": [],
            "matched_keys": [],
        }

    required = CRITERION_RUNTIME_KEYS.get(criterion, ())
    matched = [key for key in required if bool(runtime.get(key, False))]
    return {
        "supported": bool(matched),
        "source": "generic_runtime",
        "required_keys": list(required),
        "matched_keys": matched,
        "matched_ports": [],
    }


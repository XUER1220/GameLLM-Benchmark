# Per-Game D2 Test Ports

这些端口与 `evaluator/dimension2_functionality/profiles.py` 对齐。端口只提供证据，不直接加总分。

| Game ID | Test ports |
|---|---|
| `easy_snake` | `direction_control`, `food_growth`, `score_feedback`, `wall_or_self_end` |
| `easy_flappy_bird` | `flap_input`, `gravity_motion`, `pipe_scoring`, `collision_end` |
| `easy_dodge_blocks` | `player_movement`, `falling_obstacles`, `avoidance_rule`, `survival_feedback` |
| `easy_pong` | `paddle_control`, `ball_motion`, `bounce_and_score`, `point_or_game_end` |
| `medium_tetris` | `piece_control`, `gravity_drop`, `lock_and_lines`, `spawn_collision_end` |
| `medium_space_invaders` | `ship_control_fire`, `enemy_wave_motion`, `hit_score`, `lives_and_end` |
| `medium_pacman` | `grid_direction_control`, `pellet_scoring`, `power_pellet_state`, `ghost_behavior`, `win_loss` |
| `medium_super_mario_bros` | `run_jump_control`, `scrolling_world`, `block_coin_enemy_rules`, `pit_life_flag_end` |
| `hard_roguelike_dungeon` | `turn_input`, `dungeon_generation`, `combat_xp_level`, `items`, `floor_or_death_end` |
| `hard_tower_defense` | `tower_build_input`, `enemy_path_waves`, `tower_attack_rules`, `economy_upgrade`, `base_life_victory_loss` |

## Difficulty Notes

`medium_super_mario_bros` is kept in Medium because its required rules are a single fixed side-scrolling level with jump physics, camera scrolling, coins, simple patrol enemies, pits, lives, and a flag finish. It deliberately excludes Hard-level rule complexity such as power-up state transitions, hidden blocks, fireballs, multi-level progression, complex enemy AI, external sprites, audio, and animation systems.

未来若增加真正的动态测试，可向 D2 入口传入：

```python
runtime_signals = {
    "state_changed": True,
    "input_effective": True,
    "feedback_visible": True,
    "terminated": False,
    "test_ports": {
        "food_growth": {"status": "PASS"},
        "wall_or_self_end": {"status": "PARTIAL"},
    },
}
```

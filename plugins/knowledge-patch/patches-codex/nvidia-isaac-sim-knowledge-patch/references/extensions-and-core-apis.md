# Extensions, Core APIs, and application compatibility

## Migrate legacy extension namespaces

Isaac Sim 4.5 standardized extension namespaces
(`4.5.0-migration`). Update dependencies, settings paths, imports, and code
deliberately because one old extension may map to several replacements.

| Legacy extension | Replacement |
| --- | --- |
| `omni.exporter.urdf` | `isaacsim.asset.exporter.urdf` |
| `omni.importer.mjcf` | `isaacsim.asset.importer.mjcf` |
| `omni.importer.urdf` | `isaacsim.asset.importer.urdf` |
| `omni.isaac.app.selector` | `isaacsim.app.selector` |
| `omni.isaac.app.setup` | `isaacsim.app.setup` |
| `omni.isaac.ui_template` | `isaacsim.examples.ui` |
| `omni.isaac.ui` | `isaacsim.gui.components` |
| `omni.isaac.unit_converter` | `omni.usd.metrics_assembler` |
| `omni.isaac.universal_robots` | `isaacsim.robot.manipulators.examples` |
| `omni.isaac.utils` | `isaacsim.core.utils` |
| `omni.isaac.version` | `isaacsim.core.version` |
| `omni.isaac.vscode` | `isaacsim.code_editor.vscode` |
| `omni.isaac.wheeled_robots` | `isaacsim.robot.wheeled_robots` and `isaacsim.robot.wheeled_robots.examples` |
| `omni.isaac.wheeled_robots.ui` | `isaacsim.robot.wheeled_robots.ui` |
| `omni.isaac.window.about` | `isaacsim.app.about` |
| `omni.kit.property.isaac` | `isaacsim.gui.property` |
| `omni.replicator.agent.camera_calibration` | `isaacsim.replicator.agent.camera_calibration` |
| `omni.replicator.agent.core` | `isaacsim.replicator.agent.core` |
| `omni.replicator.agent.ui` | `isaacsim.replicator.agent.ui` |
| `omni.replicator.isaac` | `isaacsim.replicator.domain_randomization`, `isaacsim.replicator.examples`, and `isaacsim.replicator.writers` |

The 4.5 deprecation set without direct renames was
`omni.isaac.dynamic_control`, `omni.isaac.examples_nodes`, and
`omni.isaac.repl`; they were scheduled for removal in 5.0.

## Account for removed extensions

These extensions were removed in 4.5 (`4.5.0-migration`):

| Removed extension | Action or status |
| --- | --- |
| `omni.isaac.benchmark_environments` | Had been deprecated since 4.0. |
| `omni.isaac.cortex_sync` | Had been deprecated since 4.0. |
| `omni.isaac.dofbot` | Dofbot example is unsupported. |
| `omni.isaac.partition` | Partition tool is unsupported. |
| `omni.isaac.physics_inspector` | Use Omniverse Physics Inspector. |
| `omni.isaac.robot_benchmark` | Had been deprecated since 4.0. |
| `omni.isaac.ocs2` | Unsupported. |

ROS 1 support was removed in 5.0, and 4.5 compatibility aliases were no
longer a supported migration strategy (`5.0.0`).

Every deprecated extension was scheduled for removal in 6.0, so 5.1 projects
must eliminate remaining deprecated dependencies before that boundary
(`5.1.0`).

These 6.0 removals have no direct replacements (`6.0.0`):

- `isaacsim.app.selector`
- `isaacsim.benchmark.examples`
- `isaacsim.replicator.scene_blox`

`isaacsim.asset.browser` was also removed; use
`omni.simready.content.browser`.

## Move to experimental extension surfaces

In 6.0, established surfaces were deprecated in favor of these replacements
(`6.0.0`):

| Deprecated surface | Replacement |
| --- | --- |
| `isaacsim.replicator.mobility_gen` | `isaacsim.replicator.experimental.mobility_gen`; UI extension unchanged |
| `isaacsim.replicator.domain_randomization` | `isaacsim.replicator.experimental.domain_randomization` |
| `isaacsim.robot.wheeled_robots` | `isaacsim.robot.experimental.wheeled_robots` plus the nodes extension |
| Legacy Cortex and manipulator extensions | Experimental framework and manipulator replacements |
| Legacy Lula and motion-generation extensions | Experimental motion generation, cuMotion, and Pink extensions |

## Select the Core API and template

Isaac Sim 5.0 introduced the rewritten Core Experimental API. It preserves
the existing wrapper concepts while changing the implementation surface for
greater robustness and flexibility (`5.0.0`).

In 6.0, `isaacsim.core.api`, `isaacsim.core.prims`, and
`isaacsim.core.utils` are deprecated. Migrate to
`isaacsim.core.experimental.*` and `isaacsim.core.simulation_manager`
(`6.0.0`).

`isaacsim.examples.extension` is also deprecated. Create new project
scaffolding with:

```bash
./repo.sh template new
```

The Isaac Sim App Template repository was introduced as the application
starting point in 4.5 (`4.5.0`).

## Respect Kit compatibility boundaries

Isaac Sim 4.5 uses Kit 106.5.0 (`4.5.0`).

Isaac Sim 5.0 uses Kit 107.3.1, making applications and extensions built
against 4.5 candidates for compatibility work. Its source is available under
Apache 2.0 in `isaac-sim/IsaacSim` (`5.0.0`).

Isaac Sim 5.1 moves from
`107.3.1+isaac.206797.8131b85d.gl` to
`107.3.3+isaac.229672.69cbf6ad.gl`. The Compatibility Checker is integrated
into every installation modality rather than shipped only as a standalone
application (`5.1.0`).

Isaac Sim 6.0 moves to Kit `110.1.1`, so applications and extensions built
against earlier Kit releases must be treated as crossing another
compatibility boundary (`6.0.0`).

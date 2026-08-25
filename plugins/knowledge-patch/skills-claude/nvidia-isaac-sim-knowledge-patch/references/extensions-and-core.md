# Extensions, Core APIs, and Compatibility Boundaries

## Namespace migration

The following changes are attributed to batch `4.5.0-migration`.

Isaac Sim standardized extension namespaces in 4.5. Update extension
dependencies, settings paths, imports, and code deliberately because some
extensions split or changed naming families.

| Earlier extension | Replacement |
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

The extensions `omni.isaac.dynamic_control`,
`omni.isaac.examples_nodes`, and `omni.isaac.repl` were deprecated without
direct replacements and scheduled for removal in 5.0.

These extensions were removed in 4.5:

| Removed extension | Migration guidance |
| --- | --- |
| `omni.isaac.benchmark_environments` | It had been deprecated since 4.0. |
| `omni.isaac.cortex_sync` | It had been deprecated since 4.0. |
| `omni.isaac.dofbot` | The Dofbot example is no longer supported. |
| `omni.isaac.partition` | The partition tool is no longer supported. |
| `omni.isaac.physics_inspector` | Use Omniverse Physics Inspector. |
| `omni.isaac.robot_benchmark` | It had been deprecated since 4.0. |
| `omni.isaac.ocs2` | OCS2 is no longer supported. |

## Kit and application boundaries

Batch `4.5.0` establishes Kit 106.5.0 and introduces the Isaac Sim App Template
repository as a starting point for application projects.

Batch `5.0.0` moves to Kit 107.3.1. Treat that as a compatibility boundary for
applications and extensions built for 4.5. The Isaac Sim source is available
under Apache 2.0 in `isaac-sim/IsaacSim`. This release also introduces the
Core Experimental API, a rewritten implementation that retains existing
wrapper concepts while offering a more robust and flexible surface.

Batch `5.1.0` moves from Kit
`107.3.1+isaac.206797.8131b85d.gl` to
`107.3.3+isaac.229672.69cbf6ad.gl`. The Compatibility Checker is integrated
into every installation modality instead of being a standalone application.
All deprecated extensions were scheduled for removal at the 6.0 boundary, so
remove their dependencies before upgrading.

Batch `6.0.0` moves to Kit `110.1.1`, another compatibility boundary for
applications and extensions.

## Core and project scaffolding

In 6.0, `isaacsim.core.api`, `isaacsim.core.prims`, and
`isaacsim.core.utils` are deprecated. Move to
`isaacsim.core.experimental.*` and
`isaacsim.core.simulation_manager`.

The `isaacsim.examples.extension` project scaffold is also deprecated. Use:

```text
./repo.sh template new
```

## Experimental extension families

The following established surfaces are deprecated in 6.0:

| Deprecated surface | Replacement |
| --- | --- |
| `isaacsim.replicator.mobility_gen` | `isaacsim.replicator.experimental.mobility_gen`; the UI extension is unchanged |
| `isaacsim.replicator.domain_randomization` | `isaacsim.replicator.experimental.domain_randomization` |
| `isaacsim.robot.wheeled_robots` | `isaacsim.robot.experimental.wheeled_robots` plus its nodes extension |
| Legacy Cortex and manipulator extensions | Experimental framework and manipulator replacements |
| Legacy Lula and motion-generation extensions | Experimental motion generation, cuMotion, and Pink extensions |

These 6.0 extensions are removed:

| Removed extension | Replacement |
| --- | --- |
| `isaacsim.app.selector` | No direct replacement |
| `isaacsim.benchmark.examples` | No direct replacement |
| `isaacsim.replicator.scene_blox` | No direct replacement |
| `isaacsim.asset.browser` | `omni.simready.content.browser` |

For Replicator-specific behavior and configuration changes, also read
[synthetic-data-and-assets.md](synthetic-data-and-assets.md).

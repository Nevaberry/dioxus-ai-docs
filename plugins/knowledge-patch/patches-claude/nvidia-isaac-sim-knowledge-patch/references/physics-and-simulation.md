# Physics and Simulation

## Articulations, colliders, and diagnostics

Batch `4.5.0` adds or changes these physics capabilities:

- Inverse dynamics supports floating-base articulations, including gravity
  and Coriolis compensation and mass-matrix computation.
- New APIs compute an articulation's center of mass and centroidal momentum
  matrix.
- Signed-distance-field triangle-mesh colliders can run on the CPU. This is a
  supported option intended to improve performance in small scenes.
- Articulation mimic joints can use compliant constraints, which can improve
  stability in manipulation scenarios.
- OmniPVD captures pre- and post-simulation state, shows that data on a
  dedicated state timeline, and captures the error stream.

## Corrected physics results

After moving to 4.5, revalidate consumers and regression baselines for:

- GPU momentum in many-to-one articulation/rigid-body interactions.
- Collisions in scenes containing other self-colliding articulations.
- CPU and GPU contacts for mechanisms joined by D6 joints.
- Acceleration reports after GPU inverse-dynamics computations.

These were corrections, so retaining workarounds or golden values derived
from the earlier behavior can make upgraded tests wrong.

## Joint, deformable, and surface schemas

Batch `5.0.0` adds these PhysX schema surfaces:

- `PhysxJointAxisAPI` expresses Stribeck-like joint friction.
- `PhysxDrivePerformanceEnvelopeAPI` models speed-dependent electric-motor
  torque limits.
- A beta deformable schema replaces the previous particle-cloth and
  deformable-body workflow for both volume and surface deformables. Enable it
  in Physics preferences and restart Isaac Sim before using it.
- `PhysxSplinesSurfaceVelocityAPI` drives surface velocity along a path
  represented by `UsdGeomBasisCurves`.

Batch `5.1.0` adds an option to solve articulation collision contacts last.
This can reduce gripper penetration when joint tuning is suboptimal.

## Multitick rendering

Batch `6.0.0` lets cameras and RTX lidar render at rates and offsets driven by
physics simulation time. This is the active timing path across RTX sensors,
ROS 2, UCX, and `SimulationApp`; rendering no longer has to follow one frame
per application update.

When changing render loops, reason separately about:

- Physics ticks.
- Each sensor's render rate and offset.
- Application update cadence.
- Downstream ROS 2 or UCX publication cadence.

## Experimental Newton integration

Newton is available in 6.0 as an experimental physics engine:

- It has C++ and Python tensor APIs shaped like the PhysX APIs.
- `isaacsim.core.experimental` provides an engine-neutral physics-data
  interface.
- URDF and MJCF importers author Newton schemas when Newton is active.
- Robot policies select Newton-compatible USD variants.
- The ROS 2 bridge and tensor-backed OmniGraph nodes can use the registered
  engine.

Do not assume that selecting Newton only changes the solver. Check imported
USD schemas, policy asset variants, registered engine selection, tensor
consumers, and ROS or OmniGraph integration.

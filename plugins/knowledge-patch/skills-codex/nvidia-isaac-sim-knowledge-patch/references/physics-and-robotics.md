# Physics and robotics

## Use articulation and collision capabilities

Floating-base articulations gain inverse dynamics in 4.5, including gravity
and Coriolis compensation and mass-matrix computation. APIs also compute an
articulation's center of mass and centroidal momentum matrix (`4.5.0`).

Signed-distance-field triangle-mesh colliders can run on the CPU, providing a
supported performance option for small scenes. Articulation mimic joints can
use compliant constraints to improve stability in manipulation scenarios
(`4.5.0`).

PhysX adds an option in 5.1 to solve articulation collision contacts last.
This can reduce gripper penetration when joint tuning is suboptimal
(`5.1.0`).

## Rebaseline corrected physics results

After moving to 4.5, expect corrected results for (`4.5.0`):

- GPU momentum in many-to-one articulation/rigid-body interactions.
- Collisions in scenes containing other self-colliding articulations.
- CPU and GPU contacts for mechanisms joined by D6 joints.
- Acceleration reports after GPU inverse-dynamics computations.

Do not preserve tests or compensating logic built around the former
incorrect behavior.

## Model joint friction, motors, deformables, and surface velocity

In 5.0, `PhysxJointAxisAPI` can express Stribeck-like joint friction, and
`PhysxDrivePerformanceEnvelopeAPI` models the speed-dependent torque limits
of electric motors (`5.0.0`).

The beta deformable schema replaces the prior particle-cloth and
deformable-body workflow for volume and surface deformables. Enable it in
Physics preferences and restart Isaac Sim before use (`5.0.0`).

`PhysxSplinesSurfaceVelocityAPI` allows surface velocity to follow a path
represented by `UsdGeomBasisCurves` (`5.0.0`).

## Diagnose with OmniPVD

OmniPVD can capture pre- and post-simulation state, display it on a dedicated
state timeline, and capture the error stream (`4.5.0`).

## Select PhysX or experimental Newton

Newton is available as an experimental physics engine with C++ and Python
tensor APIs shaped like the PhysX APIs. `isaacsim.core.experimental` supplies
an engine-neutral physics-data interface (`6.0.0`).

When Newton is active:

- URDF and MJCF importers author Newton schemas.
- Robot policies select Newton-compatible USD variants.
- The ROS 2 bridge and tensor-backed OmniGraph nodes can use the registered
  engine.

## Use robot workflow tools and assets

The 5.0 robot workflow includes Robot Assembler, Gains Tuner, and Robot
Schema, plus a UR10e manipulation workflow (`5.0.0`).

Robot assets in 4.5 include variants for animation, physics simulation, and
sensor simulation. Added or refreshed models include (`4.5.0`):

- ANYbotics ANYmal V2 and V4.
- Unitree Aliengo and Laikago.
- X-Humanoid Tien Kung.
- Yaskawa Motoman NEXT NEX 10.
- RobotEra STAR1.
- TurtleBot3 Burger, including a ROS asset.
- 1X NEO.
- Nova Carter.
- Universal Robots models.

# Troubleshooting

Use this reference for known conversion, inference, transport, camera,
simulation, visualization, manipulation, and robot failures. Match the issue
to the exact package set and platform before applying a workaround.

## Model conversion and engine generation

### MobileSAM conversion under PyTorch 2.6 (4.0.0)

PyTorch 2.6 changes the `weights_only` default, which can break
MobileSAM-to-ONNX conversion. Restore the prior loading behavior for the
conversion process:

```bash
export TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1
```

Scope the environment variable to the conversion workflow when possible.

### FoundationStereo FP16 memory exhaustion (4.1.0)

FoundationStereo conversion in FP16 can run out of memory because of the
TensorRT version used by Isaac ROS 4.1. Treat this as a conversion-toolchain
constraint, not proof that the runtime camera or graph is faulty.

### SAM2 NumPy mismatch in Virtual Environment (4.1.0)

The SAM2 visualization script can fail in the Virtual Environment flow because
of a NumPy mismatch. Downgrading NumPy to 1.26.4 is a possible workaround.
The underlying Virtual Environment and Bare Metal dependency problem is fixed
in 4.5.0, so do not carry the downgrade into a newer environment without
reproducing the mismatch.

### DOPE conversion on Jetson AGX Thor (4.1.0)

The DOPE quickstart cannot convert its model from ONNX to a TensorRT Plan on
Jetson AGX Thor because the model contains unsupported layers. Repeated engine
generation with the same model and platform does not address the incompatibility.

### PeopleNet `trtexec` location (4.5.0)

If `trtexec` is absent from `/usr/src/tensorrt/bin/trtexec`, the PeopleNet
quickstart might require manual TensorRT engine generation. Verify the actual
tool location and generated engine before debugging inference graph output.

### Triton backend and repository constraints

The Triton Inference Server PyTorch backend is not supported in Isaac ROS
4.1.0.

In the DetectNet workflow (4.6.0), stale or non-Triton models in the model
repository can make Triton initialization fail. Remove unrelated models or put
Triton models under:

```text
${ISAAC_ROS_WS}/isaac_ros_assets/models/triton
```

## Missing or incorrect perception output

### RealSense and ZED boundaries (4.0.0 and 4.1.0)

For the 4.0 platform stack, the ZED SDK is incompatible with Jetson Thor and
ZED cameras were not tested. RealSense on JetPack 7 can become unstable and
stop publishing images. Use the dedicated Isaac ROS 4.1 RealSense-on-JetPack-7
setup procedure for the later package set.

### Intermittent DNN stereo output (4.5.0)

DNN stereo with RealSense, ZED, or Isaac Sim can intermittently omit disparity
or point-cloud output because the decoder does not synchronize `CameraInfo`
messages with disparity tensors. Inspect both streams and their timestamps at
the decoder boundary.

### Isaac Sim stereo visualization (4.5.0)

The Isaac Sim stereo-image-processing workflow can fail to show its point
cloud in RViz because of `PointCloud2` conversion or frame metadata. Separate
the existence of stereo output from RViz conversion and frame resolution.

### RealSense mask encoding assertion (4.6.0)

The RealSense segmentation-mask workflow sends a `mono8` infrared stream to a
DNN encoder that expects `rgb8`. The encoder terminates on a fatal assertion,
and Visual SLAM receives no mask. Confirm and correct the encoding boundary
before diagnosing Visual SLAM.

### Jetson VPI RealSense SGM failure (4.6.0)

The `isaac_ros_stereo_image_proc` RealSense SGM workflow can encounter a VPI
backend error on Jetson Orin or Thor. The error exits the component container
and prevents disparity or point-cloud output. Check container lifecycle and
VPI errors when both outputs vanish together.

### Detection and overlay caveats (4.0.0)

- DOPE can fail to detect objects in manipulation workflows.
- DetectNet can emit overlapping duplicate boxes because of its DBScan
  implementation.
- The Nvblox RealSense people-segmentation example can show an incorrect RViz
  color overlay.

Distinguish visualization defects from bad detection data by inspecting the
messages before RViz.

## Transport, compression, and simulator assets

### NITROS Bridge topics missing through DDS (4.0.0)

NITROS Bridge topics from Isaac Sim 5.1 might not arrive through DDS, breaking
the object-following manipulation simulation tutorial. Trace publication on
both sides of the bridge before changing the manipulation graph.

### Nvblox sample scene loading (4.0.0)

If the Nvblox sample scene does not load normally, open it through:

```text
Content Window → Samples → NvBlox → nvblox_sample_scene.usd
```

### Intermittent H.264 decoder starvation (4.0.0)

Running `isaac_ros_h264_decoder` alongside `isaac_ros_h264_encoder` can
intermittently leave the decoder without output. Observe the encoded stream,
decoder subscription, and output independently to localize the stall.

## GPU and hardware resource failures

### Live-camera SAM2 GPU exhaustion (4.6.0)

After an object prompt is added, `isaac_ros_segment_anything2` pipelines using
a live ZED or RealSense camera may continuously consume GPU memory until a
CUDA out-of-memory error. Monitor memory from prompt insertion onward and plan
for process recovery rather than assuming steady-state use.

### Unitree G1 hand temperature limit (4.5.0)

During real-hardware teleoperation, Unitree G1 hands can lower after several
minutes because of motor temperature limits. Check motor temperature before
treating the lowered hands as a controller, pose, or acknowledgement failure.

## Manipulation lifecycle and policy failures

### Occupied action server after a stalled goal (4.6.0)

In multi-object pick-and-place, a stalled goal may ignore cancellation or
shutdown and keep the action server occupied. Later goals are then rejected.
Inspect the existing goal and server lifecycle before retrying; a new request
does not clear the occupied server.

### Simulated UR10e and object-following failures (4.6.0)

In simulated UR10e pick-and-place:

- Grasp planning for `mac_and_cheese` can fail with
  `TRAJECTORY_OPTIMIZATION_FAILURE`, aborting the goal or reporting partial
  success.
- RT-DETR object-following can produce unstable detections.
- The reach policy can fail while loading its checkpoint.

Isolate planning, detection, and checkpoint loading as separate failure
stages; they do not share one general workaround.

### Gear Assembly test failure on Debian (4.6.0)

The Gear Assembly tutorial's pose-estimation accuracy test can fail to launch
on Debian because `parse_joint_state_from_yaml()` omits the required
`joint_names` argument. The robot then cannot move above the peg stand for the
visual pose-error check. Fix the missing argument at the call boundary before
debugging motion or pose accuracy.

## Triage sequence

1. Confirm the package set, platform, development mode, and simulator.
2. Verify that the package, camera SDK, backend, and model are supported there.
3. Inspect conversion logs and generated model artifacts.
4. Trace messages across bridge, encoder, decoder, and component-container
   boundaries.
5. Validate encodings, `CameraInfo`, timestamps, point-cloud conversion, and
   frame metadata.
6. Monitor GPU memory and robot thermals over time.
7. Inspect action and component lifecycle state before relaunching or sending
   another goal.

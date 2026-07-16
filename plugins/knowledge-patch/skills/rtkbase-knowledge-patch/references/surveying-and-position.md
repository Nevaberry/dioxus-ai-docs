# Surveying and Reference Position

## Permanent-station coordinate workflow

For a permanent base, derive fixed coordinates from a 12- or 24-hour raw
observation rather than relying on receiver survey-in. RTKBase can log receiver
raw data and convert a zipped U-Blox archive to RINEX from the Logs page. Submit
the RINEX to a precise-point-positioning service or process it with RTKLIB, then
enter the result as the base position.

The Status page calculates a live position with RTKLIB static PPP. Leaving it
open for several hours can provide a useful estimate. Computation continues for
only 15 minutes after leaving the page. On the map, the blue arrow is the moving
live estimate and the crosshair remains at the configured fixed position.

## NRCAN RINEX preset

The NRCAN RINEX preset includes Galileo observations since 2.7.0.

## ELT_RTKBase coordinate entry and validation

Entering `0.00 0.00 0.00` makes the receiver use an autonomous position averaged
for about one minute. Any other coordinate triplet requests that fixed position.

If a requested position is more than 50 m from a Unicore receiver's autonomous
solution, ELT_RTKBase substitutes the averaged solution to keep the receiver
operational and marks Main service orange. Without this protection, the Status
page may show only BeiDou and QZSS satellites.

## PPP refinement and coordinate-save effects

Changing base coordinates or another Main service setting restarts the built-in
PPP refinement from scratch.

Saving changed coordinates also stops every service. Main service restarts
automatically if it was previously running, but all other services remain stopped
and must be restarted explicitly.

## WinRtkBaseUtils RTK and HAS positioning

ELT_RTKBase's Windows utility can determine the station position directly:

- `RTK.bat` uses NTRIP v1 credentials for a nearby reference station.
- `HAS.bat` is available only for Unicore receivers and normally begins resolving
  HAS corrections in 2–10 minutes.

Both temporarily reconfigure the receiver, place coordinates on the clipboard
and in the console, and restore base mode after successful completion. RTK
results inherit the reference station's coordinate frame; HAS results are ITRF.

Turn on **Rtcm tcp service** before running either batch and turn it off
afterward. The service permits external receiver reconfiguration and should not
remain enabled. A failed or interrupted run can leave the receiver reconfigured;
apply the receiver configuration again before returning it to service.

Do not run two copies of the same batch file from one directory because they
share a temporary file.

## Full-day observation recording

For external post-processing, enable **File Service** and record exactly one
uninterrupted RTCM3 file for a complete UTC day. Stopping the device, Main
service, or File Service during that day makes the archive unsuitable for RINEX
conversion. Recording progress is visible as the file grows on the Logs page.

## RINEX conversion and final orbit products

The Logs page converts only a full-day ZIP archive. Open its pencil action,
choose the **Nrcan** or **Ign** preset, and create the RINEX file.

For CSRS-PPP, choose **ITRF** and **Static**, not NAD83 or Kinematic. Waiting about
15 days before processing allows the service to use final satellite orbit and
clock products instead of ultra-rapid products.

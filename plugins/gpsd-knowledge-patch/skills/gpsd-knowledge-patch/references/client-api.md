# libgps Client API

## gps_mainloop() — Simplified Event Loop

For applications that just need to react to each GPS update, `gps_mainloop()` provides a simpler alternative to manually calling `gps_waiting()` + `gps_read()` in a loop.

```c
int gps_mainloop(struct gps_data_t *gpsdata, int timeout,
                 void (*hook)(struct gps_data_t *gpsdata));
```

| Parameter | Description |
|-----------|-------------|
| `gpsdata` | Opened GPS data structure (from `gps_open()`) |
| `timeout` | Maximum wait time in **microseconds**; 0 = block forever |
| `hook` | Callback invoked on each data arrival |

**Returns:** -1 on timeout or error. Does not return while data keeps arriving within the timeout window.

### Example

```c
#include <gps.h>
#include <math.h>

void on_gps(struct gps_data_t *gpsdata) {
    if (gpsdata->fix.mode >= MODE_2D && isfinite(gpsdata->fix.latitude)) {
        printf("%.6f, %.6f\n", gpsdata->fix.latitude, gpsdata->fix.longitude);
    }
}

int main(void) {
    struct gps_data_t gpsdata;

    if (gps_open("localhost", "2947", &gpsdata) != 0)
        return 1;

    gps_stream(&gpsdata, WATCH_ENABLE | WATCH_JSON, NULL);
    gps_mainloop(&gpsdata, 5000000, on_gps);  /* 5s timeout */
    gps_stream(&gpsdata, WATCH_DISABLE, NULL);
    gps_close(&gpsdata);
    return 0;
}
```

## Shared-Memory Interface

For fast, lightweight local-only access, use the shared-memory interface instead of TCP sockets. Pass `GPSD_SHARED_MEMORY` as the host argument to `gps_open()`:

```c
struct gps_data_t gpsdata;
if (gps_open(GPSD_SHARED_MEMORY, NULL, &gpsdata) != 0)
    return 1;

/* Poll for data */
if (gps_read(&gpsdata, NULL, 0) > 0) {
    if (isfinite(gpsdata.fix.latitude))
        printf("%.6f, %.6f\n", gpsdata.fix.latitude, gpsdata.fix.longitude);
}
gps_close(&gpsdata);
```

### Limitations

The shared-memory interface has significant restrictions compared to the TCP socket interface:

| Feature | TCP Socket | Shared Memory |
|---------|-----------|---------------|
| `gps_stream()` | Yes | **No** |
| `gps_send()` | Yes | **No** |
| `gps_waiting()` | Yes | **No** |
| `gps_data()` | Yes | **No** |
| Device filtering | Yes | **No** |
| Activation notices | Yes | **No** |
| `gps_read()` returns | Only when new data | **Always** (returns current snapshot) |
| `gps_fd` value | Socket fd | **Always -1** |
| Remote access | Yes | **No** (local only) |

### When to Use Shared Memory

- Embedded systems where socket overhead matters
- Simple poll-based applications that don't need streaming
- Monitoring scripts that just need the latest fix
- Situations where gpsd and the client are always on the same host

### When NOT to Use Shared Memory

- You need `gps_stream()` for event-driven updates
- You need device filtering (multiple receivers)
- You need `gps_waiting()` to avoid busy-polling
- Client may run on a different host than gpsd

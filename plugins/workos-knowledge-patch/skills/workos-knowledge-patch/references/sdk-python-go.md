# Python & Go SDK Differences

## Python SDK

The Python SDK uses `WorkOSClient` (not `WorkOS`), and requires both `api_key` and `client_id` upfront:

```python
from workos import WorkOSClient

workos_client = WorkOSClient(api_key="sk_1234", client_id="client_1234")
```

Async support via separate client class:

```python
from workos import AsyncWorkOSClient

async_workos_client = AsyncWorkOSClient(api_key="sk_1234", client_id="client_1234")
```

## Go SDK

Go SDK (v6) uses per-package imports and configuration -- there is no unified client:

```go
import (
	"github.com/workos/workos-go/v6/pkg/directorysync"
	"github.com/workos/workos-go/v6/pkg/organizations"
	"github.com/workos/workos-go/v6/pkg/sso"
	"github.com/workos/workos-go/v6/pkg/usermanagement"
	"github.com/workos/workos-go/v6/pkg/webhooks"
)

func main() {
	sso.Configure("<API_KEY>", "<CLIENT_ID>")
	directorysync.SetAPIKey("<API_KEY>")
}
```

Each package provides a default client (configured via package-level functions) and a `Client` struct for custom configurations.

# Actions V1 (JavaScript-Based Actions)

Actions V1 is the JavaScript-based action system (distinct from Actions V2 webhooks). V1 actions run inline JavaScript within the Zitadel process. **Sunsetted in V5** — no new V1 features; all new implementations must use V2.

## Flow and Trigger IDs (Programmatic Setup)

| Flow | ID | Triggers |
|------|----|----------|
| External Authentication | `1` | Post Authentication (`1`), Pre Creation (`2`), Post Creation (`3`) |
| Complement Token | `2` | Pre Userinfo Creation (`4`), Pre Access Token Creation (`5`) |
| Internal Authentication | `3` | Post Authentication (`1`), Pre Creation (`2`), Post Creation (`3`) |
| Complement SAMLResponse | `4` | Pre SAMLResponse Creation (`6`) |

## `setClaim()` Behavior Gotchas

- `setClaim(key, value)` does **NOT overwrite** — if the key already exists, it silently logs to `urn:zitadel:iam:action:${actionName}:log` instead
- Keys with prefix `urn:zitadel:iam` are **silently ignored** — cannot set Zitadel's reserved claim namespace
- `appendLogIntoClaims(string)` explicitly adds to the `urn:zitadel:action:{actionName}:log` array claim

## Deprecated V1 API Patterns

- `api.v1.userinfo.setClaim()` → use `api.v1.claims.setClaim()` (Complement Token flow)
- `api.metadata` array → use `api.v1.user.appendMetadata(key, value)` (all auth flows)

## Built-In Modules

Actions V1 provides three built-in modules (NOT Node.js — custom runtime):

### HTTP (`zitadel/http`)
Custom fetch that does **NOT** match the Fetch API spec:
```js
let http = require('zitadel/http')
let resp = http.fetch('https://api.example.com/data', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer token' },
  body: { key: 'value' }  // JSON object, NOT stringified
})
// resp.status (number), resp.body (string), resp.json(), resp.text()
// Allowed methods: GET, POST, PUT, DELETE only
```

### Log (`zitadel/log`)
```js
let logger = require('zitadel/log')
logger.log('info message')
logger.warn('warning message')
logger.error('error message')
```

### UUID (`zitadel/uuid`)
```js
let uuid = require('zitadel/uuid')
uuid.v4()  // random UUID
uuid.v5(uuid.namespaceURL, 'https://example.com')  // deterministic
// Predefined: uuid.namespaceDNS, uuid.namespaceURL, uuid.namespaceOID, uuid.namespaceX500
```

## SAML Response Customization

V1 actions can customize SAML attributes via the Complement SAMLResponse flow:
```js
function setSamlAttribute(ctx, api) {
  api.v1.attributes.setCustomAttribute('department',
    'urn:oasis:names:tc:SAML:2.0:attrname-format:basic',
    'Engineering')
}
```
`setCustomAttribute(key, nameFormat, ...values)` adds custom attributes to the SAML response.

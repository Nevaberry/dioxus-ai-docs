# Privacy, Permissions, and App Data

## Health sensors

Apps targeting API 36 on Android 16 (`api-36`) must replace `BODY_SENSORS`
with granular health permissions such as `READ_HEART_RATE`, and replace
`BODY_SENSORS_BACKGROUND` with `READ_HEALTH_DATA_IN_BACKGROUND`. This also
affects Wear OS APIs and health foreground services. A mobile app must declare
an activity that displays its privacy-policy rationale; otherwise the health
permission is revoked.

## MediaStore and selected-media access

For API 36-targeted apps, `MediaStore.getVersion()` returns an app-specific
value. Treat it as an opaque change token. Do not parse it or infer device
information from it.

When the user grants access only to selected photos and videos, the Android 16
photo picker preselects app-owned media. The user can deselect those items,
immediately revoking access despite app ownership.

## SMS one-time passwords

On Android 17 (`api-37`), WebOTP messages are withheld for three hours from
every app except the domain-verified recipient and exempt handlers, regardless
of target SDK. API 37-targeted apps also lose immediate access to ordinary
OTP-bearing SMS. During the delay, both `SMS_RECEIVED_ACTION` and SMS-provider
queries are filtered. Use SMS Retriever or SMS User Consent for OTP flows.

## Contacts provider queries

For API 37-targeted apps, `ContactsContract.Data` no longer exposes
`ACCOUNT_NAME`, `ACCOUNT_TYPE`, or `ACCOUNT_TYPE_AND_DATA_SET`. Obtain them
from `RawContacts` by joining on `RAW_CONTACT_ID`.

Without `READ_CONTACTS`, `Data` queries also enforce `StrictColumns` and
`StrictGrammar`; incompatible SQL is rejected with an exception.

## Explicit URI grants

Android 18 will stop implicitly granting URI access for `ACTION_SEND`,
`ACTION_SEND_MULTIPLE`, and `ACTION_IMAGE_CAPTURE`. Android 17 provides
`StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` to locate
dependencies before that change. Add `FLAG_GRANT_READ_URI_PERMISSION` to send
intents. For image capture, add both read and write grant flags.

## Session location access

Jetpack can embed a system-rendered location button that grants precise
location for the current session without a permission dialog. Declare
`USE_LOCATION_BUTTON`; do not treat its session grant as persistent location
permission.

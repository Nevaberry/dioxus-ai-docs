# Installed Application Detection

Use this reference when calling `navigator.getInstalledRelatedApps()` or
configuring the two-way declarations that authorize Android, Windows, and PWA
installation detection.

## Query boundaries

`navigator.getInstalledRelatedApps()` is available only in a secure HTTPS
context. It returns installed applications that satisfy both requirements:

- the website declares the application in its manifest; and
- the installed application has a verified relationship with the website.

The query considers only the first three entries in `related_applications`.
It cannot enumerate arbitrary applications installed on the device.

Results include details such as `platform`, `id`, and `url`. Android results
also include `version`.

```js
const related = await navigator.getInstalledRelatedApps?.() ?? [];
const androidVersion = related.find(
  app => app.platform === "play" && app.id === "com.example.twa"
)?.version;
```

The manifest fields `min_version` and `fingerprints` are specified as filters,
but no browser implements either filter on any platform. An older or
certificate-mismatched application may therefore still appear in results.

## Android installed-app detection

Android Chrome 80+ requires declarations in both directions.

### Application declares website

The Android application declares the website through a Digital Asset Links
`asset_statements` resource. The relation is
`delegate_permission/common.handle_all_urls`.

```xml
<!-- AndroidManifest.xml -->
<meta-data android:name="asset_statements"
           android:resource="@string/asset_statements" />

<!-- strings.xml -->
<string name="asset_statements">[{\"relation\":[\"delegate_permission/common.handle_all_urls\"],\"target\":{\"namespace\":\"web\",\"site\":\"https://example.com\"}}]</string>
```

### Website declares application

The website's manifest uses platform `play` and the Android package ID:

```json
{
  "related_applications": [
    { "platform": "play", "id": "com.example.twa" }
  ]
}
```

## UWP detection

Windows Chrome or Edge 85+ uses an App URI Handler plus a package-family
declaration.

### Package registers each host

The UWP package registers `windows.appUriHandler` for every website host:

```xml
<uap3:Extension Category="windows.appUriHandler">
  <uap3:AppUriHandler>
    <uap3:Host Name="example.com" />
  </uap3:AppUriHandler>
</uap3:Extension>
```

### Website verifies package

The website serves an extensionless `windows-app-web-link` file either at the
site root or under `/.well-known/`. The file names the Package Family Name:

```json
[
  {
    "packageFamilyName": "MyApp_9jmtgj1pbbz6e",
    "paths": ["*"]
  }
]
```

The web manifest uses platform `windows` and appends `!App` to that Package
Family Name:

```json
{
  "related_applications": [
    {
      "platform": "windows",
      "id": "MyApp_9jmtgj1pbbz6e!App"
    }
  ]
}
```

## In-scope PWA self-detection

An installed PWA can identify itself from a page on the same origin and inside
its manifest scope:

- Android Chrome 84+ supports this form; and
- desktop Chrome or Edge 140+ supports it.

When the page has only this self-declaration and calls from outside the
manifest scope, the query returns `[]`.

Declare the related application with:

- platform `webapp`;
- the PWA manifest URL; and
- the declared or browser-computed web app ID.

The `id` is required on desktop but not on Android.

```json
{
  "scope": "/",
  "start_url": "/?utm_source=home_screen",
  "related_applications": [{
    "platform": "webapp",
    "url": "/manifest.json",
    "id": "https://example.com/?utm_source=home_screen"
  }]
}
```

## Cross-scope or cross-origin PWA detection

This form remains Android-only on Chrome 84+. It allows a page outside the
PWA's scope, including a page on another origin, to query the PWA.

The PWA origin serves `/.well-known/assetlinks.json` with relation
`delegate_permission/common.query_webapk`. Its target is the checking
website's manifest URL, not the PWA's manifest URL:

```json
[{
  "relation": ["delegate_permission/common.query_webapk"],
  "target": {
    "namespace": "web",
    "site": "https://www.example.com/manifest.json"
  }
}]
```

The checking website declares the PWA's absolute manifest URL as a `webapp`
related application:

```json
{
  "related_applications": [{
    "platform": "webapp",
    "url": "https://app.example.com/manifest.json"
  }]
}
```

Together, these declarations provide the mutual relationship required by the
query while preserving the distinction between the checking manifest and the
installed PWA manifest.

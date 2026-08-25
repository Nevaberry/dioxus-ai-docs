# Installed Application Detection

## Query boundaries and returned data

On HTTPS, `navigator.getInstalledRelatedApps()` returns installed apps that
both appear in the page's manifest and have a verified relationship with the
page (batch `pwa-installation-detection`).

It considers only the first three `related_applications` entries. It cannot
enumerate arbitrary apps installed on the device.

Returned entries include details such as:

- `platform`;
- `id`;
- `url`;
- `version` for Android results.

The manifest defines `min_version` and `fingerprints` as filters, but no
browser implements either filter for any platform. A lower-version or
certificate-mismatched app may therefore still be returned. Check relevant
returned details in application logic rather than trusting these filters.

```js
const related = await navigator.getInstalledRelatedApps?.() ?? [];
const androidVersion = related.find(
  app => app.platform === "play" && app.id === "com.example.twa"
)?.version;
```

## Android native-app detection

Android Chrome 80 and later requires declarations in both directions.

The Android app declares the website through a Digital Asset Links
`asset_statements` resource using
`delegate_permission/common.handle_all_urls`:

```xml
<!-- AndroidManifest.xml -->
<meta-data android:name="asset_statements"
           android:resource="@string/asset_statements" />

<!-- strings.xml -->
<string name="asset_statements">[{\"relation\":[\"delegate_permission/common.handle_all_urls\"],\"target\":{\"namespace\":\"web\",\"site\":\"https://example.com\"}}]</string>
```

The website declares the Android package ID with platform `play`:

```json
{
  "related_applications": [
    { "platform": "play", "id": "com.example.twa" }
  ]
}
```

## Windows UWP detection

Windows Chrome or Edge 85 and later requires a UWP App URI Handler and a
website declaration.

The UWP package registers `windows.appUriHandler` for each website host:

```xml
<uap3:Extension Category="windows.appUriHandler">
  <uap3:AppUriHandler>
    <uap3:Host Name="example.com" />
  </uap3:AppUriHandler>
</uap3:Extension>
```

The site publishes an extensionless `windows-app-web-link` file at the root or
under `/.well-known/`. It names the Package Family Name:

```json
[
  {
    "packageFamilyName": "MyApp_9jmtgj1pbbz6e",
    "paths": ["*"]
  }
]
```

The web manifest uses platform `windows` and appends `!App` to that name:

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

## Same-scope PWA self-detection

An installed PWA can detect itself from a page on the same origin and within
its manifest scope:

- Android Chrome 84 and later;
- desktop Chrome or Edge 140 and later.

With only this self-declaration, a call outside the manifest scope returns
`[]`.

Declare platform `webapp`, the PWA manifest URL, and the manifest-declared or
browser-computed web app ID. The `id` is required on desktop but not Android.

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

Detection from a page outside the PWA's scope or on another origin remains
Android-only, starting with Chrome 84.

The PWA origin serves `/.well-known/assetlinks.json` with
`delegate_permission/common.query_webapk`. Its target is the checking
website's manifest URL, not the PWA's manifest:

```json
[
  {
    "relation": ["delegate_permission/common.query_webapk"],
    "target": {
      "namespace": "web",
      "site": "https://www.example.com/manifest.json"
    }
  }
]
```

The checking website declares the PWA's absolute manifest URL:

```json
{
  "related_applications": [{
    "platform": "webapp",
    "url": "https://app.example.com/manifest.json"
  }]
}
```

Keep the two URLs straight: the asset link targets the querying site's
manifest, while `related_applications` points to the installed PWA's manifest.

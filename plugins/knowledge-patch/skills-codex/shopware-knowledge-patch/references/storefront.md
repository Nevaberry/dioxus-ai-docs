# Storefront

## Header, footer, and ESI

### Storefront chrome uses ESI

Store API `Cached*Route` decorators are removed. Header and footer render
through `/header` and `/footer`, the new `layout/header.html.twig` and
`layout/footer.html.twig` entry points, and `base_esi_header` /
`base_esi_footer`. Custom data must travel as query parameters on the
corresponding ESI request.

### Page data belongs in pagelets

`GenericPageLoader`, `Page`, and `ErrorTemplateStruct` no longer carry
header/footer and payment/shipping data. Extend `HeaderPageletLoader` or
`FooterPageletLoader` and their loaded events. Pass the now-required
`serviceMenu` when constructing `FooterPagelet`.

In header/footer templates use `header` / `footer`, `context.currency`,
`context.languageInfo`, and `shopware.navigation.*`. Override moved base blocks
in the new layout entry points. `showStagingBanner` is renamed to
`shopware.showStagingBanner`.

### ESI failures are visible

Errors from `/header` and `/footer` ESI renders are no longer ignored. To keep
the old behavior deliberately, override the relevant template blocks and
remove `ignore_errors: false` from their `render_esi` calls.

## Routing and navigation

### Use `activeRoute`

Replace Twig `controllerName` / `controllerAction`, JavaScript
`window.controllerName` / `window.actionName`, and `.is-ctl-*` / `.is-act-*`
selectors with `activeRoute`, `window.activeRoute`, and
`.is-active-route-*`. Route names contain dots; turn those dots into dashes for
the CSS class.

```twig
{% set routeClass = activeRoute|replace({'.': '-'}) %}
```

### Allow arbitrary route names

Storefront controller routes need not have a `frontend`, `widgets`, or
`payment` prefix when their names are allowlisted.

```yaml
storefront:
  router:
    allowed_routes: [swag.test.foo-bar]
```

### Vary dynamic navigation cache keys

`NavigationRoute` caches default category levels per sales channel and loads
every level on the active category path. If an extension varies navigation
dynamically, subscribe to `CategoryLevelLoaderCacheKeyEvent` and add the
varying input; otherwise cached navigation can be served for the wrong state.
`buildName()` is deprecated because all navigation responses now share
`NavigationRoute::ALL_TAG`.

### Offcanvas categories

Overrides of `layout/navigation/offcanvas/categories.html.twig` must calculate
`hasChildren` inside the category loop and render a folder link only for a
category that has children.

### Typed domain loaders (since 6.7.13.0)

`AbstractDomainLoader::load()` is deprecated for removal in 6.8. Decorators
should implement `loadDomains()`, which returns a URL-keyed `DomainCollection`
of `DomainStruct` objects. Consumers should call `$domains->get($url)` and use
object properties such as `$domain->url`, not array access.

## Forms, addresses, and validation

### Address-manager template variable (since 6.7.13.0)

Themes and plugins extending the address-manager modal list, create, or item
templates must replace the deprecated Twig variable `type` with `addressType`
before 6.8.

### Form violations use snippets (since 6.7.13.0)

Custom constraints used by contact, newsletter, or revocation forms should
define `error.<violation-code>` in
`Resources/snippet/storefront.<locale>.json`. `FormController` resolves
validation messages from the active Storefront language's snippets rather
than Symfony's validator catalogue.

### FormFieldToggle button labels (since 6.7.13.0)

On the controlling field, `data-form-field-toggle-button-target` selects a
related button and `data-form-field-toggle-button-text` gives its alternate
text when the toggle target is hidden. Omitting either optional attribute
keeps the earlier `FormFieldToggle` behavior.

### Registration address validation

Malformed billing or shipping address values during registration produce HTTP
400 validation errors rather than a server error. Customer and order address
first and last names support 255 characters. Custom validators and schemas
should follow those contracts.

## Snippets, themes, and Twig

### Prefer country-agnostic snippets

Rename translations such as `en-GB` to `en` and update
`snippet_set.base_file`. Region-specific names remain only as a compatibility
path. The validation command is `translation:validate`; `snippets:validate` is
removed in the next major, and `SnippetValidator` becomes internal.

### Theme runtime configuration

Rendered theme configuration lives in `theme_runtime_config` and is rebuilt
during theme refresh. Replace `CachedResolvedConfigLoader` with
`ResolvedConfigLoader`, and `ThemeAssignmentException` with
`ThemeException::themeAssignmentException()`.

Starting in 6.8, theme label and help text must be Administration snippets
named
`sw-theme.<technicalName>.<tab>.<block>.<section>.<field>.label|helpText`.
API consumers should use structured-field `labelSnippetKey` /
`helpTextSnippetKey` and
`ThemeConfigurationService::getPlainThemeConfiguration()` /
`getThemeConfigurationFieldStructure()`.

### Theme and review extension points

`ThemeFileImporterInterface` / `ThemeFileImporter` and
`StorefrontController::setTwig()` are removed. Resolve theme files through
`ThemeFilesystemResolver`. Replace Storefront product-review loader, event,
hook, and result classes with the corresponding Core
`Product\SalesChannel\Review` types.

### Complete Shopware Twig forms

The Storefront Twig integration adds the `sw_block`, `sw_source`, and
`sw_include` functions and the `sw_use`, `sw_embed`, `sw_from`, and `sw_import`
tokens.

### Breadcrumb context and separator

Pass `SalesChannelContext`, not its inner Core context, to
`sw_breadcrumb_full` and `sw_breadcrumb_full_by_id`.

```twig
{{ sw_breadcrumb_full(category, context) }}
```

Breadcrumb separators use `--bs-breadcrumb-divider`. Replace the deprecated
`layout_breadcrumb_placeholder` override by passing `breadcrumbDivider` from
`layout_breadcrumb_container`.

## Media, images, and feeds

### Product-export URL encoding

`ProductExportRenderer::renderBody()` RFC 3986-encodes `MediaEntity::url` and
`MediaThumbnailEntity::url` values supplied to the body template. Remove
manual encoding from direct media URL expressions to prevent double encoding.
Headers, footers, non-media strings, and URLs assembled wholly inside Twig are
unaffected.

```twig
<g:image_link>{{ product.cover.media.url }}</g:image_link>
<link>{{ product.customFields.external_url|sw_encode_url }}</link>
```

### Headless image minimum height (since 6.7.13.0)

New image CMS elements have an empty `minHeight`. Storefront applies a minimum
height only when `config.displayMode.value === 'cover'`; headless renderers
should use the same condition rather than the former `340px` default in
standard or stretch modes.

### Product-feed crawl rules (since 6.7.13.0)

The default `robots.txt` adds `Allow: /*referringSalesChannel=` alongside its
blanket query-string disallow. This lets product-feed landing pages be crawled
while their clean canonical URL is indexed. Plugins with other tracking
parameters can add equivalent rules through `RobotsPageLoadedEvent`.

### Configurable robots metadata

The Basic Information setting can provide Storefront
`<meta name="robots">` content.

## Interaction and markup

### Accessibility contracts

Storefront overrides must account for these changes:

- Product cards remove the image anchor and add `stretched-link` to the
  product-name anchor; the base font becomes `1rem`.
- Currency and language options are submit buttons, not hidden radios. Modal
  triggers are buttons using the new `*Modal` snippet keys and tag parameters.
- Cart and order line-item roots are `<li>` elements inside `<ul>` wrappers.
  Pagination uses anchors with `data-page`, not radio inputs.
- `{% sw_icon %}` emits `aria-hidden="true"` by default. Set
  `ariaHidden: false` only when the icon carries accessible meaning itself.

### Video and cookie overrides

Video templates must replace a shared `block_image_inner` override with
`block_vimeo_video_inner` or `block_youtube_video_inner`. Vimeo and YouTube
also have separate consent entries. `CookieConfiguration` uses delegated
events, so `_registerEvents()` overrides must handle dynamically inserted
offcanvas links.

### Alert markup

The `sw-skin-alert` mixin, `alert-has-icon` styling, and inner `.alert-content`
wrapper are removed. Use Bootstrap alert variables and target the remaining
`.alert-content-container`.

### Browser and query-string support

Browser support follows Browserslist `defaults` unless `BROWSERSLIST`
overrides it. Native `URLSearchParams` replaces the removed `query-string`
package.

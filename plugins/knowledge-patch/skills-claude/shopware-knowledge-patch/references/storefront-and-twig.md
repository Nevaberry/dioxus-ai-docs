# Storefront, Themes, Routing, and Twig

## Route, navigation, and domain contracts

### Active route state

Replace Twig `controllerName` / `controllerAction`, JavaScript `window.controllerName` / `window.actionName`, and `.is-ctl-*` / `.is-act-*` selectors with `activeRoute`, `window.activeRoute`, and `.is-active-route-*`. Route names contain dots; replace them with dashes when constructing the CSS class.

```twig
{% set routeClass = activeRoute|replace({'.': '-'}) %}
```

### Arbitrary route names

Storefront controller route names no longer need a `frontend`, `widgets`, or `payment` prefix when allowlisted:

```yaml
storefront:
  router:
    allowed_routes: [swag.test.foo-bar]
```

### Domain loader collections (6.7.13.0)

`AbstractDomainLoader::load()` is deprecated for removal in 6.8. Decorators should implement `loadDomains()`, returning a URL-keyed `DomainCollection` of `DomainStruct` objects. Consumers should use `$domains->get($url)` and properties such as `$domain->url`, not array access.

### Dynamic navigation cache keys

`NavigationRoute` caches default category levels for a sales channel and loads every level on the active category path. Extensions whose navigation varies dynamically must subscribe to `CategoryLevelLoaderCacheKeyEvent` and add the varying input, or cached navigation can be served for the wrong state. `buildName()` is deprecated because navigation responses share `NavigationRoute::ALL_TAG`.

### Offcanvas child detection

Overrides of `layout/navigation/offcanvas/categories.html.twig` must set `hasChildren` inside the category loop and render a folder link only when the category has children.

## Header, footer, ESI, and cache behavior

### ESI pagelets

`GenericPageLoader`, `Page`, and `ErrorTemplateStruct` no longer carry header/footer and payment/shipping data. Extend `HeaderPageletLoader` or `FooterPageletLoader` and their loaded events. Pass the now-required `serviceMenu` when constructing `FooterPagelet`.

In header and footer templates, use `header` / `footer`, `context.currency`, `context.languageInfo`, and `shopware.navigation.*`. Override moved base blocks in the new layout entry points. `showStagingBanner` is now `shopware.showStagingBanner`.

Header and footer render through `/header` and `/footer`, `layout/header.html.twig` and `layout/footer.html.twig`, and `base_esi_header` / `base_esi_footer`; custom data must be query parameters on the corresponding ESI request. The former `Cached*Route` Store API decorators are removed.

### Visible ESI failures

Errors from `/header` and `/footer` ESI renders are no longer ignored. To deliberately restore the previous behavior, override the relevant template blocks and remove `ignore_errors: false` from their `render_esi` calls.

### Rule-aware cache hashes

With `CACHE_REWORK` enabled, `sw-cache-hash` omits rules that cannot affect product prices. Storefront output driven by other custom rules must contribute IDs through `ResolveCacheRelevantRuleIdsExtension`, directly or through a rule area marked on the DAL association with `RuleAreas`. `RuleAreas::CATEGORY_AREA` and `LANDING_PAGE_AREA` are deprecated.

## Templates, forms, and snippets

### Address-manager variables (6.7.13.0)

Themes and plugins extending address-manager modal list, create, or item templates must replace deprecated Twig variable `type` with `addressType` before 6.8.

### Form violation snippets (6.7.13.0)

Custom constraints used by contact, newsletter, or revocation forms should define `error.<violation-code>` in `Resources/snippet/storefront.<locale>.json`. `FormController` resolves messages through the active Storefront language's snippets rather than Symfony's validator catalogue.

### FormFieldToggle button labels (6.7.13.0)

On the controlling field, `data-form-field-toggle-button-target` selects a related button and `data-form-field-toggle-button-text` provides alternate text when the toggle target is hidden. Omitting either optional attribute preserves previous `FormFieldToggle` behavior.

### Country-agnostic snippet files

Rename translations such as `en-GB` to `en` and update `snippet_set.base_file`. Region-specific names remain only as a compatibility path. The validation command is `translation:validate`; `snippets:validate` is removed in the next major, and `SnippetValidator` becomes internal.

### Complete Twig dialect forms

Storefront Twig adds `sw_block`, `sw_source`, and `sw_include` functions plus `sw_use`, `sw_embed`, `sw_from`, and `sw_import` tokens.

## Breadcrumbs, metadata, and URLs

### Breadcrumb separator

Breadcrumb separators use `--bs-breadcrumb-divider`. Replace deprecated `layout_breadcrumb_placeholder` overrides by passing `breadcrumbDivider` from `layout_breadcrumb_container`.

### Breadcrumb context

Pass `SalesChannelContext`, not its inner Core context, to `sw_breadcrumb_full` and `sw_breadcrumb_full_by_id`:

```twig
{{ sw_breadcrumb_full(category, context) }}
```

### Product-export media URL encoding

`ProductExportRenderer::renderBody()` RFC 3986-encodes `MediaEntity::url` and `MediaThumbnailEntity::url` before body-template rendering. Remove manual encoding from direct media URL expressions to prevent double encoding. Headers, footers, non-media strings, and URLs assembled wholly inside Twig are unaffected.

```twig
<g:image_link>{{ product.cover.media.url }}</g:image_link>
<link>{{ product.customFields.external_url|sw_encode_url }}</link>
```

### Product-feed crawling (6.7.13.0)

The default `robots.txt` adds `Allow: /*referringSalesChannel=` beside the blanket query-string disallow. This lets product-feed landing pages be crawled while their clean canonical URL is indexed. Plugins with other tracking parameters can add equivalent rules through `RobotsPageLoadedEvent`.

### Configurable robots metadata

The Basic Information setting can provide Storefront `<meta name="robots">` content.

## CMS and media element rendering

### Image element minimum height (6.7.13.0)

New image CMS elements have an empty `minHeight`. Apply a minimum height only when `config.displayMode.value === 'cover'`; headless renderers must not rely on the former `340px` default in standard or stretch modes.

### Video and cookie overrides

Video templates must replace the shared `block_image_inner` override with `block_vimeo_video_inner` or `block_youtube_video_inner`. Vimeo and YouTube have separate consent entries. `CookieConfiguration` uses delegated events, so `_registerEvents()` overrides must handle dynamically inserted offcanvas links.

### Cookie groups

`/store-api/cookie-groups` returns registered groups through `CookieRoute`. Plugins must replace `CookieProviderInterface` decorators with a `CookieGroupCollectEvent` listener adding `CookieGroup` / `CookieEntry` structs. Twig cookie fields use `name` and `description`, not `snippet_name` and `snippet_description`.

## Theme and accessibility migrations

### Theme runtime configuration

Rendered theme configuration lives in `theme_runtime_config` and is regenerated during theme refresh. Replace `CachedResolvedConfigLoader` with `ResolvedConfigLoader` and `ThemeAssignmentException` with `ThemeException::themeAssignmentException()`.

Starting in 6.8, theme labels and help text must be Administration snippets named `sw-theme.<technicalName>.<tab>.<block>.<section>.<field>.label|helpText`. API consumers should use structured-field `labelSnippetKey` / `helpTextSnippetKey` and `ThemeConfigurationService::getPlainThemeConfiguration()` / `getThemeConfigurationFieldStructure()`.

### Theme and review extension types

`ThemeFileImporterInterface`, `ThemeFileImporter`, and `StorefrontController::setTwig()` are removed. Resolve theme files through `ThemeFilesystemResolver`. Replace Storefront product-review loader, event, hook, and result classes with corresponding Core `Product\SalesChannel\Review` types.

### Accessibility markup

Theme overrides must follow these structural contracts:

- Product cards remove the image anchor, add `stretched-link` to the product-name anchor, and use a `1rem` base font.
- Currency and language choices are submit buttons rather than hidden radios. Modal triggers are buttons using the new `*Modal` snippet keys and tag parameters.
- Cart and order line-item roots are `<li>` elements in `<ul>` wrappers. Pagination uses anchors with `data-page`, not radio inputs.
- `{% sw_icon %}` emits `aria-hidden="true"` by default. Set `ariaHidden: false` only when the icon itself carries accessible meaning.

### Alert markup

The `sw-skin-alert` mixin, `alert-has-icon` styling, and inner `.alert-content` wrapper are removed. Use Bootstrap alert variables and target the remaining `.alert-content-container`.

### Browser and query-string support

Browser support follows Browserslist `defaults` unless `BROWSERSLIST` overrides it. Native `URLSearchParams` replaces the removed `query-string` package.

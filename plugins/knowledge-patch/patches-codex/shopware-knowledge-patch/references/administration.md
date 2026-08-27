# Administration

## Build tooling, Vue, and state

### Vite and native Vue 3

Administration extensions with a custom `webpack.config.js` must migrate to
`vite.config.js` and distribute a 6.7-specific build. Components are async by
default, so guard template refs or use `@vue:mounted`; the Vue 2 compatibility
layer is gone.

### Pinia replaces Vuex

Core stores use `Shopware.Store`. Register a Pinia store with
`Shopware.Store.register()` and mutate its state in actions rather than Vuex
mutations. Remaining Vuex code must use `mapVuexState`, `mapVuexMutations`,
`mapVuexGetters`, and `mapVuexActions`. Use `$t` instead of the compatibility
`$tc` path.

### Production sourcemaps are opt-in

Set `GENERATE_SOURCEMAPS=true` with `NODE_ENV=production` for Administration,
extension, Storefront-component Vite, and Storefront webpack builds. Other
values keep the production default of no sourcemaps; non-production builds
always generate them.

```bash
GENERATE_SOURCEMAPS=true NODE_ENV=production composer build:js:admin
GENERATE_SOURCEMAPS=true NODE_ENV=production composer build:js:storefront
```

## Meteor component migration

The 6.8 migration replaces these basic components:

- `sw-popover` → `mt-floating-ui`
- `sw-tabs` → `mt-tabs`
- `sw-select-field` → `mt-select`
- `sw-textarea-field`, `sw-datepicker`, `sw-password-field`,
  `sw-colorpicker`, `sw-external-link`, `sw-skeleton-bar`, `sw-email-field`,
  `sw-url-field`, `sw-progress-bar`, `sw-button`, `sw-icon`, `sw-card`,
  `sw-text-field`, `sw-switch-field`, `sw-number-field`, `sw-loader`, and
  `sw-checkbox-field` → their `mt-*` equivalents.

Most value controls use `model-value`, `v-model`, and `update:model-value`.
Labels and hints become string props, and many bespoke props and events vanish.
Exceptions:

- `mt-checkbox` uses `checked`, `v-model:checked`, `update:checked`, and
  `partial`.
- `mt-switch` uses `checked` and `removeTopMargin`.
- Select options use `{label, value}`.
- Tabs use `items` plus `new-item-active`.
- Floating UI uses `isOpened`.

Map the `danger` button variant to `critical`, express ghost styling with the
`ghost` prop, and give icons explicit `16px`, `24px`, or `32px` sizes. In 6.7,
the compatibility `deprecated` prop renders the legacy Shopware component.
`mt-tooltip` content may contain strings or ordinary HTML, not Vue components.

## CMS extension points

### CMS block component names

Administration CMS rendering honors a block configuration's `component`
value and falls back to `sw-cms-block-${block.type}`. Custom block definitions
must set `component` correctly.

### Renamed CMS entity-select blocks (since 6.7.13.0)

Move overrides before 6.8:

- Buy box: `sw_cms_element_buy_box_config_product_variant_label` →
  `sw_cms_element_buy_box_config_product_selection_label`, and
  `sw_entity_single_select_base_results_list_result_label` →
  `sw_cms_element_buy_box_config_product_select_result_item_inner`.
- Cross-selling: `sw_entity_single_select_variant_selected_item` →
  `sw_cms_element_cross_selling_config_content_products_selection_label`,
  `sw_entity_single_select_variant_result_item` →
  `sw_cms_element_cross_selling_config_content_products_select_result_item`,
  and `sw_entity_single_select_base_results_list_result_label` →
  `sw_cms_element_cross_selling_config_content_products_select_result_item_inner`.
- Product box: `sw_entity_single_select_base_results_list_result_label` →
  `sw_cms_element_product_box_config_product_select_result_item_inner`; new
  blocks are `sw_cms_element_product_box_config_product_selection_label` and
  `sw_cms_element_product_box_config_product_select_result_item`.
- Product description/reviews:
  `sw_entity_single_select_variant_selected_item` →
  `sw_cms_element_product_description_reviews_config_product_selection_label`,
  `sw_entity_single_select_variant_result_item` →
  `sw_cms_element_product_description_reviews_config_product_select_result_item`,
  and `sw_entity_single_select_base_results_list_result_label` →
  `sw_cms_element_product_description_reviews_config_product_select_result_item_inner`.
- Product slider: `sw_entity_single_select_base_results_list_result_label` →
  `sw_cms_element_product_slider_config_content_products_select_result_item_inner`;
  new blocks are
  `sw_cms_element_product_slider_config_content_products_selection_label` and
  `sw_cms_element_product_slider_config_content_products_select_result_item`.
- Product cross-selling assignment:
  `sw_entity_single_select_base_results_list_result_label` →
  `sw_product_cross_selling_assignment_select_result_item_inner`; the new
  result-item block is `sw_product_cross_selling_assignment_select_result_item`.

## Rule-condition UI

### Generic condition rendering

`cartLineItemInCategory` and `cartLineItemPurchasePrice` render through
`sw-condition-generic`. The components `sw-condition-line-item-in-category`,
`sw-condition-line-item-purchase-price`, and `sw-condition-is-net-select` are
removed in 6.8. Product-stream overrides must move from
`sw_product_stream_filter` / `sw_product_stream_filter_container` to
`sw_condition_base` / `sw_condition_base_content`.

### Entity error store

`sw-condition-base` reads `rule_condition` errors centrally, and
`sw-condition-field-errors` renders the labelled summary. Custom conditions
must stop using local `mapPropertyErrors('condition', ...)`,
`conditionValue*Error`, or `currentError` implementations. The `hasError`,
error-class, and arrow-color APIs on the type/operator selects were removed.

### Match-all toggle

Line-item conditions expose the “all / at least one” toggle only when
`getConfig()` supplies the corresponding `isMatchAny` configuration. The
Administration no longer shows it for every line-item condition (since
6.7.13.0).

## Removed or renamed extension points

### Twig extension points expiring in 6.8

Stop overriding `sw_integration_list_introduction`,
`sw_settings_mailer_headline_agent`, the `sw-settings-cache-index` members
`processSuccess` / `resetButtons()`, and these search-setting blocks:

- `sw_settings_search_excluded_search_terms_empty_state_image`
- `sw_settings_search_view_live_search_search_icon_wrapper`
- `sw_settings_search_view_live_search_search_icon`
- `sw_settings_search_search_index_warning_top`
- `sw_settings_search_search_index_rebuild_progress_text`
- `sw_settings_search_searchable_content_customfields_state_image`
- `sw_settings_search_searchable_content_general_state_image`
- `sw_settings_search_searchable_show_example`
- `sw_settings_search_searchable_show_example_link_element`

### Dashboard extension points

`sw-dashboard-statistics` has no replacement. Move component sections from
`sw-chart-card__before` / `sw-chart-card__after` to
`sw-dashboard__before-content` / `sw-dashboard__after-content`. Dashboard order
and date-range data sets are gone, so extensions must query the Admin API.

### Notifications moved to Core

Notification entity, definition, collection, and controller types move from
`Shopware\Administration` to `Shopware\Core\Framework\Notification`; the HTTP
route is unchanged.

### Legacy cache-control hooks (since 6.7.13.0)

`BeforeCacheControlEvent`, `AdministrationController::CACHE_ID_HEADER`, and
`AdministrationController::CACHE_ID_ADMINISTRATION` are deprecated for removal
in 6.8. There is no replacement because `CACHE_REWORK`, default in 6.8, returns
cache-control headers directly to the client.

## Snippet editing

The snippet detail page identifies JSON-backed values and can mark a database
override for deletion on save. This restores inheritance from the language
file and allows later file updates to flow through (since 6.7.13.0).

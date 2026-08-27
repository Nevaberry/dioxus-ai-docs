# Administration Extensions

## Cache and extension-point removals

### Legacy cache-control hooks (6.7.13.0)

`BeforeCacheControlEvent`, `AdministrationController::CACHE_ID_HEADER`, and `AdministrationController::CACHE_ID_ADMINISTRATION` are deprecated for removal in 6.8. There is no replacement because `CACHE_REWORK`, the default behavior in 6.8, returns cache-control headers directly to the client.

### Expiring Twig extension points

Stop targeting `sw_integration_list_introduction`, `sw_settings_mailer_headline_agent`, the `sw-settings-cache-index` members `processSuccess` / `resetButtons()`, and these search-setting blocks before 6.8:

- `sw_settings_search_excluded_search_terms_empty_state_image`
- `sw_settings_search_view_live_search_search_icon_wrapper`
- `sw_settings_search_view_live_search_search_icon`
- `sw_settings_search_search_index_warning_top`
- `sw_settings_search_search_index_rebuild_progress_text`
- `sw_settings_search_searchable_content_customfields_state_image`
- `sw_settings_search_searchable_content_general_state_image`
- `sw_settings_search_searchable_show_example`
- `sw_settings_search_searchable_show_example_link_element`

## Rule Builder and condition rendering

### Match-all availability (6.7.13.0)

Line-item conditions expose the "all / at least one" toggle only when their `getConfig()` supplies the corresponding `isMatchAny` configuration. Administration no longer shows it for every line-item condition.

### Purchase-price rule type (6.7.13.0)

`LineItemPurchasePriceRule` (`cartLineItemPurchasePrice`) persists `type: gross|net` instead of the `isNet` boolean. Code creating or interpreting the rule configuration must use `type`.

### Generic condition rendering

`cartLineItemInCategory` and `cartLineItemPurchasePrice` render through `sw-condition-generic`. `sw-condition-line-item-in-category`, `sw-condition-line-item-purchase-price`, and `sw-condition-is-net-select` are removed in 6.8. Product-stream overrides must move from `sw_product_stream_filter` / `sw_product_stream_filter_container` to `sw_condition_base` / `sw_condition_base_content`.

### Central condition errors

`sw-condition-base` reads `rule_condition` errors centrally, and `sw-condition-field-errors` renders the labelled summary. Custom conditions must stop using local `mapPropertyErrors('condition', ...)`, `conditionValue*Error`, or `currentError` implementations. The `hasError`, error-class, and arrow-color APIs on type and operator selects were removed.

## CMS and snippets

### Snippet inheritance restoration (6.7.13.0)

The snippet detail page identifies JSON-backed values and can mark a database override for deletion on save. This restores inheritance from the language file and lets later file updates flow through.

### CMS template block renames (6.7.13.0)

Move generic entity-select overrides to component-specific replacements before 6.8:

- Buy box: `sw_cms_element_buy_box_config_product_variant_label` → `sw_cms_element_buy_box_config_product_selection_label`; `sw_entity_single_select_base_results_list_result_label` → `sw_cms_element_buy_box_config_product_select_result_item_inner`.
- Cross-selling: `sw_entity_single_select_variant_selected_item` → `sw_cms_element_cross_selling_config_content_products_selection_label`; `sw_entity_single_select_variant_result_item` → `sw_cms_element_cross_selling_config_content_products_select_result_item`; `sw_entity_single_select_base_results_list_result_label` → `sw_cms_element_cross_selling_config_content_products_select_result_item_inner`.
- Product box: `sw_entity_single_select_base_results_list_result_label` → `sw_cms_element_product_box_config_product_select_result_item_inner`; new blocks are `sw_cms_element_product_box_config_product_selection_label` and `sw_cms_element_product_box_config_product_select_result_item`.
- Product description/reviews: `sw_entity_single_select_variant_selected_item` → `sw_cms_element_product_description_reviews_config_product_selection_label`; `sw_entity_single_select_variant_result_item` → `sw_cms_element_product_description_reviews_config_product_select_result_item`; `sw_entity_single_select_base_results_list_result_label` → `sw_cms_element_product_description_reviews_config_product_select_result_item_inner`.
- Product slider: `sw_entity_single_select_base_results_list_result_label` → `sw_cms_element_product_slider_config_content_products_select_result_item_inner`; new blocks are `sw_cms_element_product_slider_config_content_products_selection_label` and `sw_cms_element_product_slider_config_content_products_select_result_item`.
- Product cross-selling assignment: `sw_entity_single_select_base_results_list_result_label` → `sw_product_cross_selling_assignment_select_result_item_inner`; the new result-item block is `sw_product_cross_selling_assignment_select_result_item`.

### Configured CMS block components

Administration CMS rendering uses a block config's `component` value and falls back to `sw-cms-block-${block.type}`. Custom block definitions must set `component` correctly.

## Vue, Vite, and state management

### Vite and native Vue 3

Administration extensions with a custom `webpack.config.js` must migrate to `vite.config.js` and distribute a 6.7-specific build. Components are async by default; guard template refs or use `@vue:mounted`. The Vue 2 compatibility layer is gone.

### Pinia and compatibility helpers

Core stores use `Shopware.Store`. Register a Pinia store with `Shopware.Store.register()` and mutate state in actions rather than defining Vuex mutations. Remaining Vuex code must use `mapVuexState`, `mapVuexMutations`, `mapVuexGetters`, and `mapVuexActions`. Use `$t` instead of the compatibility `$tc` path.

## Meteor component migration

The 6.8 migration replaces these components with `mt-*` equivalents: `sw-popover`, `sw-tabs`, `sw-select-field`, `sw-textarea-field`, `sw-datepicker`, `sw-password-field`, `sw-colorpicker`, `sw-external-link`, `sw-skeleton-bar`, `sw-email-field`, `sw-url-field`, `sw-progress-bar`, `sw-button`, `sw-icon`, `sw-card`, `sw-text-field`, `sw-switch-field`, `sw-number-field`, `sw-loader`, and `sw-checkbox-field`. Examples include `mt-floating-ui`, `mt-tabs`, and `mt-select`.

Most value controls use `model-value`, `v-model`, and `update:model-value`; labels and hints become string props, and many bespoke field props and events disappear. Exceptions include:

- `mt-checkbox`: `checked`, `v-model:checked`, `update:checked`, and `partial`.
- `mt-switch`: `checked` and `removeTopMargin`.
- Select options: `{label, value}`.
- Tabs: `items` plus `new-item-active`.
- Floating UI: `isOpened`.

Map button variant `danger` to `critical` and use a `ghost` prop for ghost styling. Set icons to explicit `16px`, `24px`, or `32px` sizes to preserve old sizing. The compatibility `deprecated` prop renders the legacy Shopware component in 6.7. `mt-tooltip` content can contain strings or ordinary HTML, not Vue components.

## Moved and removed Administration features

### Notifications

Notification entity, definition, collection, and controller types move from `Shopware\Administration` to `Shopware\Core\Framework\Notification`. The HTTP route is unchanged.

### Dashboard extension points

`sw-dashboard-statistics` has no replacement. Component sections move from `sw-chart-card__before` / `__after` to `sw-dashboard__before-content` / `__after-content`. Dashboard order and date-range data sets are gone, so extensions must query the Admin API.

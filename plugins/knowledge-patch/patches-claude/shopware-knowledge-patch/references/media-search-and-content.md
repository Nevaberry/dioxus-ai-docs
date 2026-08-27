# Media, Search, and Content

## Media generation and paths

### Per-thumbnail post-processing (6.7.13.0)

`Shopware\Core\Content\Media\Event\ThumbnailGeneratedEvent` fires after each thumbnail is written. It exposes the media and thumbnail IDs, path, MIME type, and `FilesystemOperator`; subscribers can read, optimize, and replace the file.

JPEG thumbnails are progressive. Batch generation logs and cleans up an individual failure before continuing, although `ThumbnailService::updateThumbnails()` still surfaces single-media failures.

### MIME-aware media path hooks

Set `ResolveRemoteThumbnailUrlExtension::$mediaEntity` instead of deprecated `mediaPath` and `mediaUpdatedAt`. Replace `MediaPathChangedEvent::media()` / `thumbnail()` with `mediaWithMimeType()` / `thumbnailWithMimeType()`.

## Product streams and listings

### Individual variants from product streams (6.7.13.0)

The `product_stream.display_as_group` / `displayAsGroup` boolean defaults to true. Disable it to prevent matching variants from being grouped or remapped. `ProductStreamBuilderInterface` and `buildFilters()` are deprecated for 6.8; extend `AbstractProductStreamBuilder` and use `enrichCriteria()` as the extension point.

### Search settings and plural SEO resolution

The minimum search-term length is read from database configuration rather than `.env`. `SeoResolverData::get()` is deprecated because it silently returns one match. Use `getAll()` and update every matching entity when attaching SEO URLs.

## Mail simulation

### Custom form data (6.7.13.0)

Declare custom form variables as `FormDataObjectType` in the event's available data, then populate simulations through `MailDataSimulatorFormDataEvent`:

```php
public function provideFormData(MailDataSimulatorFormDataEvent $event): void
{
    if ($event->flowEventName === 'my_form.send' && $event->variableName === 'myFormData') {
        $event->setData(['field' => 'value']);
    }
}
```

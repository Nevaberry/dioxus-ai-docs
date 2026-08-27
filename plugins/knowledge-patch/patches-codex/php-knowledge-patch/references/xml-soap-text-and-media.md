# XML, SOAP, Text, and Media

## XML handlers and deprecated object association

Source batch: `8.4-migration`.

XML handler setters enforce an effective `callable|string|null` handler type.
Legacy method-name strings are resolved only after `xml_set_object()` associates
an object.

Migrate to direct callables such as `[$handler, 'method']`.
`xml_set_object()` and non-callable method-name strings passed to
`xml_set_*()` are deprecated.

`xml_parser_free()` is deprecated because its handle object is freed
automatically (source batch `8.5-migration`).

## DOM and XPath

### Object restrictions

Source batch: `8.4-migration`.

`DOMXPath` can no longer be cloned. `DOMImplementation::getFeature()` has been
removed. `DOM_PHP_ERR` and obsolete DOM encoding and configuration properties
are deprecated.

`GMP` is final and cannot be subclassed.

### Native XPath callables

Source batch: `8.4.0`.

`DOMXPath::registerPhpFunctions()` accepts any callable.
`DOMXPath::registerPhpFunctionNs()` registers callbacks under a namespace so
XPath can call them with native function syntax instead of
`php:function('name')`.

## XMLReader, XMLWriter, and XSL validation

Source batch: `8.4-migration`.

XMLReader, XMLWriter, and XSL operations throw for invalid encodings, null
bytes, incompatible objects, or failed PHP callbacks where applicable.

Class constants supplied by XMLReader now declare types. Reflection or tooling
that assumed those internal constants were untyped must account for the type
metadata.

## XSL parameters, callbacks, and limits

### Quote-safe parameters and native callbacks

Source batch: `8.4.0`.

XSLT parameters may contain both single and double quotes without failing.
`XSLTProcessor::registerPhpFunctions()` accepts any callable.

`XSLTProcessor::$maxTemplateDepth` and
`XSLTProcessor::$maxTemplateVars` control recursion depth and variable limits
during XSL template evaluation.

### Namespace-aware parameters

Source batch: `8.5.0`.

The `namespace` argument of `XSLTProcessor::getParameter()`,
`setParameter()`, and `removeParameter()` takes effect. It applies when `name`
is unqualified. Clark notation or a QName instead supplies the namespace
through its URI or prefix.

## SOAP members, handlers, and builds

### Member type migrations

Source batch: `8.4-migration`.

`SoapClient::$httpurl` and `$sdl` are `Soap\Url` and `Soap\Sdl` objects, and
`$typemap` is an array. Replace resource checks on those members with null
checks.

### Function registration

Source batch: `8.4-migration`.

Passing `SOAP_FUNCTIONS_ALL` or another integer to
`SoapServer::addFunction()` is deprecated. Pass an array of function names,
such as a flattened `get_defined_functions()` result.

### Optional session dependency

Source batch: `8.4-migration`.

SOAP optionally depends on the session extension. A build without session but
with `--enable-rtld-now` can fail at startup when SOAP is loaded. Avoid that
flag combination or load the session extension.

## SOAP mappings, dates, schemas, and faults

### Namespaced class maps

Source batch: `8.4.0`.

SOAP class-map keys may use Clark notation to disambiguate identically named
types from different namespaces.

```php
$classMap = ['{http://example.com}foo' => 'FooClass'];
```

### Date and time serialization

Source batch: `8.4.0`.

`DateTimeInterface` instances supplied for `xsd:datetime` and similar SOAP
elements are serialized as date/time values rather than as empty strings.

### Schema enumerations and Reason language

Source batch: `8.5.0`.

`SoapClient::__getTypes()` includes enumeration cases. SOAP 1.2 Reason Text
supports `xml:lang`, exposed through a new optional `lang` parameter on
`SoapFault::__construct()` and `SoapServer::fault()`.

### URI parsing for requests

Source batch: `8.5-migration`.

`SoapClient::__doRequest()` has an optional URI-parser class argument. `null`
keeps `parse_url()`. `Uri\Rfc3986\Uri` and `Uri\WhatWg\Url` select the new
parser backends.

## SimpleXML iteration and XPath

Calling methods such as `asXML()` or `getName()`, or casting a
`SimpleXMLElement` to string, no longer resets its iterator. Loops that
accidentally relied on that reset must call `rewind()` explicitly (source batch
`8.4-migration`).

`SimpleXMLElement::xpath()` warns and returns `false` when the expression
produces something other than a node set (source batch `8.5-migration`).

## mbstring indices and Unicode data

Source batch: `8.4-migration`.

For strings with encoding errors, `mb_substr()` interprets character indices
consistently with other mbstring functions, so offsets from `mb_strpos()` can
be reused.

SJIS-Mac indices refer to the Unicode code points produced by conversion,
including characters that expand to multiple code points.

mbstring uses Unicode 17.0 data (source batch `8.5-migration`). Malformed
mbstring maps or encodings now raise `ValueError`.

## Intl collation and list formatting

Intl regular collation sort handles numeric strings like the standard
`SORT_REGULAR` (source batch `8.5-migration`).

`IntlListFormatter`, available with ICU 67 or newer, formats localized AND, OR,
or unit lists in wide, short, or narrow forms using its `TYPE_*` and `WIDTH_*`
constants (source batch `8.5.0`).

## EXIF and image dimensions

Source batch: `8.5.0`.

EXIF supports `OffsetTime*` tags and HEIF/HEIC. `getimagesize()` recognizes
HEIF/HEIC and, with ext-libxml, SVG.

Image-size results include `width_unit` and `height_unit`. They default to
pixels but may differ. SVG is also recognized by
`image_type_to_extension()` and `image_type_to_mime_type()`.

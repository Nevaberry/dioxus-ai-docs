# XML, SOAP, and XSL

## XML parser and writer APIs

### Deprecated XML entry points (8.4-migration)

`xml_set_object()` is deprecated, as are non-callable method-name strings passed
to `xml_set_*()`. `DOM_PHP_ERR` and obsolete DOM encoding and configuration
properties are deprecated. `xml_parser_free()` is deprecated
(8.5-migration) because the parser object is freed automatically.

### Handler callable migration (8.4-migration)

XML handler setters enforce an effective `callable|string|null` handler type.
Legacy method-name strings resolve only after `xml_set_object()` associates an
object. Migrate to direct callables such as `[$handler, 'method']`, because both
that association API and non-callable strings are deprecated.

### XML exception tightening (8.4-migration)

XMLReader and XMLWriter operations throw for invalid encodings, null bytes, or
incompatible objects where applicable. Validate external input and update code
that expected warnings or permissive coercion.

## DOM and XPath

### Object restrictions (8.4-migration)

`DOMXPath` cannot be cloned, and `DOMImplementation::getFeature()` has been
removed. Separately, `GMP` is final and cannot be subclassed.

### Native XPath callables (8.4.0)

`DOMXPath::registerPhpFunctions()` accepts any callable.
`DOMXPath::registerPhpFunctionNs()` registers a callback under a namespace, so
XPath can use native function syntax instead of `php:function('name')`.

## SimpleXML

### Iterator position (8.4-migration)

Calling methods such as `asXML()` or `getName()`, or casting a
`SimpleXMLElement` to string, no longer resets its iterator. Loops that relied
on an implicit reset must call `rewind()` explicitly.

### XPath result types (8.5-migration)

`SimpleXMLElement::xpath()` warns and returns `false` when the expression
produces something other than a node set.

## SOAP

### Function registration and member types (8.4-migration)

Replace an integer such as `SOAP_FUNCTIONS_ALL` passed to
`SoapServer::addFunction()` with an array of function names, such as a
flattened `get_defined_functions()` result.

`SoapClient::$httpurl` and `$sdl` are `Soap\Url` and `Soap\Sdl` objects, and
`$typemap` is an array. Replace resource checks for these members with null
checks.

### SOAP/session build interaction (8.4-migration)

SOAP optionally depends on the session extension. A build without session but
with `--enable-rtld-now` can fail at startup when SOAP loads. Avoid that flag
combination or load the session extension.

### Namespaced class maps (8.4.0)

SOAP class-map keys may use Clark notation to distinguish types with the same
name in different namespaces.

```php
$classMap = ['{http://example.com}foo' => 'FooClass'];
```

### Date/time serialization (8.4.0)

`DateTimeInterface` instances supplied for `xsd:datetime` and related SOAP
elements serialize as date/time values rather than empty strings.

### Selectable URI parsing (8.5-migration)

`SoapClient::__doRequest()` has an optional URI-parser class argument. `null`
keeps `parse_url()`; `Uri\Rfc3986\Uri` and `Uri\WhatWg\Url` select the new
parser backends.

### Schema enums and reason languages (8.5.0)

`SoapClient::__getTypes()` includes enumeration cases. SOAP 1.2 Reason Text
supports `xml:lang`, exposed by a new optional `lang` parameter on
`SoapFault::__construct()` and `SoapServer::fault()`.

## XSLT

### Validation and callback failures (8.4-migration)

XSL operations throw for null bytes, incompatible objects, invalid encodings,
or failed PHP callbacks where applicable. Update callers that expected only a
warning or permissive behavior.

### Quote-safe parameters and native callbacks (8.4.0)

XSLT parameters may contain both single and double quotes.
`XSLTProcessor::registerPhpFunctions()` accepts any callable.

### Evaluation limits (8.4.0)

`XSLTProcessor::$maxTemplateDepth` and `$maxTemplateVars` control template
recursion depth and variable limits.

### Namespace-aware parameters (8.5.0)

The `namespace` argument of `XSLTProcessor::getParameter()`, `setParameter()`,
and `removeParameter()` takes effect when `name` is unqualified. Clark notation
or a QName instead supplies the namespace through its URI or prefix.

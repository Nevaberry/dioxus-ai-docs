# Testing, Quality, and Problems

## Test report formats and structure

### Accept millisecond XML timestamps (8.13.0)

JUnit XML test-event timestamps have millisecond precision. Report consumers
must parse values such as:

```xml
<testsuite timestamp="2024-02-03T12:34:56.789">
```

### Preserve skipped-test reasons (8.14.0)

When an assumption violation skips a JUnit 4, JUnit Platform, or TestNG test,
Gradle includes the reason in both HTML and JUnit XML.

### Interpret hierarchical HTML and XML reports (9.3.0)

HTML mirrors framework structure: nested classes live under the enclosing
class, parameterized methods own their invocations, suites own their classes,
and synthetic package containers are removed. Output stays with the individual
test that emitted it. Nested-class XML filenames remain
`TEST-OuterClass$InnerClass.xml`, and suite XML emits only class reports.

`TestReport` and the Test Report Aggregation Plugin preserve each report input
as a separate HTML tab instead of merging overlapping structures. This keeps
identically named suites and classes attributable to their source project.

### Capture JUnit data and attachments (9.4.0)

JUnit Platform `TestReporter` entries and files emitted during construction,
setup, test execution, or teardown appear in reports. HTML has Data and
Attachments tabs. XML maps key-values to `<properties/>` and files to
`[[ATTACHMENT|/path/to/file]]`.

### Sort HTML reports (9.6.1)

Click report columns to sort, reverse, and restore their original order. Tests,
Failures, Skipped, and Duration initially sort descending; Success rate
initially sorts ascending.

## Custom test execution and metadata

### Emit Gradle reports for externally executed tests (8.13.0)

Plugin and platform authors can inject `TestEventReporterFactory` to produce
Gradle binary results and HTML for tests outside the built-in test machinery.
Reporters support timestamped `metadata(...)`, nested
`reportTestGroup(...)`, and `reportTest(...)` events. Close reporters after
recording their terminal event.

```java
try (TestEventReporter test = testEventReporterFactory.createTestEventReporter(
        "custom-test", binaryResultsDirectory, htmlReportDirectory)) {
    test.started(Instant.now());
    test.metadata(Instant.now(), "engine", "custom");
    test.succeeded(Instant.now());
}
```

### Discover non-class JUnit Platform definitions (9.4.0)

Custom `TestEngine` definitions need not have a test class. Configure
`testDefinitionDirs`; Cucumber can then execute feature files directly without
an empty suite class or JUnit extension:

```kotlin
tasks.named<Test>("test") {
    testDefinitionDirs.from("src/test/definitions")
}
```

### Consume structured test metadata (9.4.0)

`Test.addTestMetadataListener(TestMetadataListener)` exposes attachment and
other reported-data events to build logic without parsing standard output.

### Surface framework initialization failures (9.7.0)

TestNG, JUnit 4, and JUnit Platform initialization failures bypass the default
granularity filter and appear in console output. Explicitly omitting `FAILED`
from `testLogging.events` still silences them. Tooling API and Build Scan
consumers can identify these failures through
`TestFailureDetails.isFrameworkFailure()`.

### Match TestNG's thread-pool factory interface (9.7.0)

`threadPoolFactoryClass` supports TestNG 7.10+, where the class must implement
`org.testng.IExecutorServiceFactory`. With TestNG 7.0 through 7.9, it must
implement `org.testng.thread.IExecutorFactory`.

## Problems API and diagnostics

### Attach arbitrary structured problem data (8.14.0)

`ProblemSpec.additionalData(...)` accepts a typed interface extending
`AdditionalData`. Its model may contain Provider API properties, bean-style
fields, collections, and nested objects:

```java
public interface SomeData extends AdditionalData {
    Property<String> getSome();
    List<String> getNames();
    void setNames(List<String> names);
}

problem.additionalData(SomeData.class, data -> {
    data.getSome().set("some");
    data.setNames(Collections.singletonList("moreData"));
});
```

Tooling API consumers call `CustomAdditionalData.get(Class)` with a view
interface mirroring the producer model. This returns typed structured data
without parsing a serialized representation.

### Render structured problems in the console (9.3.0)

`--warning-mode=all` renders relevant Problems API entries and their build
location in the console while preserving the link to the HTML Problems report.

### Understand source-location limits (9.7.0)

Gradle captures source locations for up to 2,050 problems per build. The first
50 retain full stack traces; the next 2,000 use cheaper capture and stop at the
originating script. `--warning-mode=all` removes the count limit, but locations
after the first 50 still do not retain the full call chain.

## Plugin validation and quality reports

### Configure additional PMD formats per task (9.4.0)

`Pmd` tasks can emit CSV, Code Climate, and SARIF. They are disabled by default
and must be set on the task rather than the `pmd` extension:

```kotlin
tasks.pmdMain {
    reports {
        csv.required = true
        codeClimate.required = true
        sarif.required = true
    }
}
```

### Correct `@Optional` misuse (9.6.1)

`validatePlugins` reports targeted errors when `@Optional` lacks an input or
output annotation or is combined with `@Internal`. Add the appropriate
input/output annotation, or use `@Internal` alone for an ignored property.

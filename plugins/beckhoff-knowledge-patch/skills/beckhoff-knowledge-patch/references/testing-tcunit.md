# Unit Testing (TcUnit)

## TcUnit Framework Pattern
TcUnit is the standard xUnit testing framework for TwinCAT 3 (v1.3.1, MIT license). Each test suite is a function block extending `TcUnit.FB_TestSuite`. Tests run inside the PLC runtime cycle.

```iecst
// Test suite FB — one per logical group of tests
FUNCTION_BLOCK FB_MotorTests EXTENDS TcUnit.FB_TestSuite

// Call all test methods from the FB body
METHOD RunTests
    TestStartSetsRunning();
    TestStopClearsRunning();

// Each test method follows: TEST → act → assert → TEST_FINISHED
METHOD TestStartSetsRunning
    TEST('StartSetsRunningFlag');

    // Arrange & Act
    fbMotor.Start();

    // Assert — type-specific methods: AssertEquals_BOOL, AssertEquals_INT,
    // AssertEquals_DINT, AssertEquals_LREAL, AssertEquals_STRING, etc.
    AssertEquals_BOOL(Expected := TRUE,
                      Actual := fbMotor.bRunning,
                      Message := 'Motor should be running after Start');

    TEST_FINISHED();
```

## Multi-Cycle Tests
PLC tests often need multiple scan cycles (e.g., waiting for a TON timer). Omit `TEST_FINISHED()` until the condition is met — TcUnit keeps the test active across cycles.

```iecst
METHOD TestTimerExpires
VAR_INST
    nCycle : INT;
    tonTest : TON;
END_VAR
    TEST('TimerExpiresAfter100ms');

    tonTest(IN := TRUE, PT := T#100MS);
    nCycle := nCycle + 1;

    IF tonTest.Q THEN
        AssertTrue(Condition := TRUE,
                   Message := 'Timer should have expired');
        TEST_FINISHED();    // only call when done
    ELSIF nCycle > 200 THEN
        AssertTrue(Condition := FALSE,
                   Message := 'Timeout — timer never expired');
        TEST_FINISHED();
    END_IF
```

## Test Runner Registration
Instantiate all test suite FBs in a `PRG_TEST` program. TcUnit auto-discovers them — no manual registration needed. Add `PRG_TEST` to a separate PLC task (or call from MAIN during testing).

```iecst
PROGRAM PRG_TEST
VAR
    fbMotorTests  : FB_MotorTests;
    fbSensorTests : FB_SensorTests;
END_VAR

fbMotorTests();
fbSensorTests();
```

## TcUnit-Runner (CI/CD)
TcUnit-Runner is a separate .NET console application that automates: open TwinCAT project → activate config → run PLC → collect results → output to console. Returns non-zero exit code on test failure. Integrates with Jenkins, Azure DevOps, GitHub Actions.

Install path for Build 4026+: `C:\TwinCAT\Functions\TF6000-ADS-Communication\TcUnit\`

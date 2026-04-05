# MQTT & IoT Integration (TF6701)

## FB_IotMqttClient — Core MQTT Client
Library: `Tc3_IotBase`. The client FB must be called cyclically via `Execute()` to maintain broker connection and receive messages. All connection parameters are input properties set before calling `Execute`.

```iecst
VAR
    fbMqttClient   : FB_IotMqttClient;
    fbMessageQueue : FB_IotMqttMessageQueue;
    bSetParameter  : BOOL := TRUE;
    bConnect       : BOOL := TRUE;
END_VAR
// Set connection params (once)
IF bSetParameter THEN
    bSetParameter               := FALSE;
    fbMqttClient.sHostName      := '192.168.1.10';  // broker IP or hostname
    fbMqttClient.nHostPort      := 1883;             // default MQTT port
    fbMqttClient.ipMessageQueue := fbMessageQueue;   // attach receive queue
    // Optional: .sClientId, .sUserName, .sUserPassword, .nKeepAlive (default 60s)
END_IF
fbMqttClient.Execute(bConnect);  // MUST call cyclically
```

## Publish — Pointer-Based Payload
`Publish()` takes a raw pointer to payload data. Use `ADR()` and `LEN2()` for strings. Returns TRUE on success.

```iecst
IF fbMqttClient.bConnected THEN
    sPayloadPub := CONCAT('RPM:', TO_STRING(nCurrentSpeed));
    fbMqttClient.Publish(
        sTopic       := sTopicPub,            // STRING(255)
        pPayload     := ADR(sPayloadPub),
        nPayloadSize := LEN2(ADR(sPayloadPub)) + 1,  // +1 for null terminator
        eQoS         := TcIotMqttQos.AtMostOnceDelivery,  // 0, 1, or 2
        bRetain      := FALSE,
        bQueue       := FALSE);
END_IF
```

## Subscribe + Message Queue Receive Pattern
Subscribe once after connection. Messages accumulate in `FB_IotMqttMessageQueue` — dequeue one per cycle via `FB_IotMqttMessage`.

```iecst
VAR
    bSubscribed : BOOL;
    sTopicSub   : STRING(255) := 'plant/sensor/#';   // wildcard supported
    {attribute 'TcEncoding':='UTF-8'}
    sTopicRcv   : STRING(255);
    {attribute 'TcEncoding':='UTF-8'}
    sPayloadRcv : STRING(255);
    fbMessage   : FB_IotMqttMessage;
END_VAR
IF fbMqttClient.bConnected AND NOT bSubscribed THEN
    bSubscribed := fbMqttClient.Subscribe(
        sTopic := sTopicSub,
        eQoS   := TcIotMqttQos.AtMostOnceDelivery);
END_IF

// Dequeue one message per cycle
IF fbMessageQueue.nQueuedMessages > 0 THEN
    IF fbMessageQueue.Dequeue(fbMessage := fbMessage) THEN
        fbMessage.GetTopic(pTopic := ADR(sTopicRcv), nTopicSize := SIZEOF(sTopicRcv));
        fbMessage.GetPayload(pPayload := ADR(sPayloadRcv),
                             nPayloadSize := SIZEOF(sPayloadRcv),
                             bSetNullTermination := FALSE);
    END_IF
END_IF
```

Note: Use `{attribute 'TcEncoding':='UTF-8'}` on received topic/payload STRING variables to handle UTF-8 encoded MQTT data correctly.

## JSON Serialization for MQTT Payloads
Library: `Tc3_JsonXml`. Use `FB_JsonSaxWriter` with `FB_JsonReadWriteDataType.AddJsonValueFromSymbol` to auto-serialize a STRUCT to JSON.

```iecst
// fbJson : FB_JsonSaxWriter;  fbJsonDataType : FB_JsonReadWriteDataType
fbJson.ResetDocument();
fbJsonDataType.AddJsonValueFromSymbol(fbJson, 'ST_SensorData',
    SIZEOF(stValues), ADR(stValues));
sJsonDoc := fbJson.GetDocument();
// For large documents: fbJson.CopyDocument(sJsonDoc, SIZEOF(sJsonDoc));

fbMqttClient.Publish(sTopic := sTopicPub,
    pPayload := ADR(sJsonDoc),
    nPayloadSize := LEN2(ADR(sJsonDoc)),
    eQoS := TcIotMqttQos.AtMostOnceDelivery,
    bRetain := FALSE, bQueue := FALSE);
```

## JSON Deserialization — Parsing Incoming Payloads
Use `FB_JsonDomParser` to parse received JSON, then extract fields with `HasMember` / typed getters. Alternative: `SetJsonToSymbol` deserializes directly into a matching STRUCT (member names must match JSON keys).

```iecst
// For JSON: {"deviceId":"sensor-03","temperature":23.5,"status":1}
fbJsonDoc.ParseDocument(sPayloadRcv);  // fbJsonDoc : FB_JsonDomParser
IF fbJsonDoc.HasMember('temperature') THEN
    fTemperature := fbJsonDoc.GetDoubleFromMember('temperature');
END_IF
IF fbJsonDoc.HasMember('deviceId') THEN
    sDeviceId := fbJsonDoc.GetStringFromMember('deviceId');
END_IF
```

## TLS/SSL Secure Connection
Set `stTLS` on the client before connecting. Port 8883 is standard MQTTS. Certs must exist on the TwinCAT target filesystem.

```iecst
// TLS with CA + client certificate (mutual authentication)
fbMqttClient.stTLS.sCA      := 'c:\TwinCAT\3.1\Target\Certificates\ca.crt';
fbMqttClient.stTLS.sCert    := 'c:\TwinCAT\3.1\Target\Certificates\client.crt';
fbMqttClient.stTLS.sKeyFile := 'c:\TwinCAT\3.1\Target\Certificates\client.key';
fbMqttClient.nHostPort      := 8883;  // standard MQTTS port
// Server-only verification (no client cert): set only stTLS.sCA
// Pre-shared key alternative: stTLS.sPskIdentity + stTLS.sPskKey (hex-encoded)
```

## Last Will and Testament (LWT)
The broker publishes the will message on ungraceful disconnect. Set will properties before `Execute()`. Pair with a retained "birth" publish for online/offline status.

```iecst
// Will — broker sends 'OFFLINE' if client drops unexpectedly
fbMqttClient.sWillTopic   := 'plant/status/plc1';
fbMqttClient.sWillMessage := 'OFFLINE';
fbMqttClient.eWillQoS     := TcIotMqttQos.AtLeastOnceDelivery;
fbMqttClient.bWillRetain  := TRUE;  // new subscribers see last status

// Birth — publish 'ONLINE' with retain after connecting
IF fbMqttClient.bConnected AND NOT bBirthSent THEN
    sPayloadPub := 'ONLINE';
    fbMqttClient.Publish(sTopic := 'plant/status/plc1',
        pPayload := ADR(sPayloadPub), nPayloadSize := LEN2(ADR(sPayloadPub)) + 1,
        eQoS := TcIotMqttQos.AtLeastOnceDelivery, bRetain := TRUE, bQueue := FALSE);
    bBirthSent := TRUE;
END_IF
```

## Multiple Subscriptions, Topic Routing, and Reconnection
Call `Subscribe()` once per topic after connection. Wildcards: `#` matches all sub-levels, `+` matches one level. Subscriptions are lost on disconnect -- use a rising-edge detect on `bConnected` to re-subscribe. The client reconnects automatically via `Execute(TRUE)`; `nKeepAlive` (default 60s) controls disconnect detection speed.

```iecst
fbMqttClient.Execute(bConnect);

// Rising edge on bConnected — resubscribe after initial connect or reconnect
IF fbMqttClient.bConnected AND NOT bConnectedPrev THEN
    fbMqttClient.Subscribe(sTopic := 'plant/sensors/#',      eQoS := TcIotMqttQos.AtMostOnceDelivery);
    fbMqttClient.Subscribe(sTopic := 'plant/commands/plc1',   eQoS := TcIotMqttQos.AtLeastOnceDelivery);
    fbMqttClient.Subscribe(sTopic := 'plant/config/+/update', eQoS := TcIotMqttQos.AtMostOnceDelivery);
END_IF
bConnectedPrev := fbMqttClient.bConnected;

// Route by topic when dequeuing
IF fbMessageQueue.Dequeue(fbMessage := fbMessage) THEN
    fbMessage.GetTopic(pTopic := ADR(sTopicRcv), nTopicSize := SIZEOF(sTopicRcv));
    IF FIND(sTopicRcv, 'commands') > 0 THEN
        // handle command
    ELSIF FIND(sTopicRcv, 'config') > 0 THEN
        // handle config update
    END_IF
END_IF
```

## Error Handling
Check `fbMqttClient.bError` and `fbMqttClient.hrErrorCode` after `Execute()` for connection/communication failures. Reset errors by calling `Execute(FALSE)` then `Execute(TRUE)` to force a fresh connection attempt.

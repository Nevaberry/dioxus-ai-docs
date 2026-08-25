# Extensions, serialization, and XCom

## Plugin import boundary

Plugins cannot register operators, sensors, hooks, or executors for import
through Airflow's plugin namespace. These are ordinary Python classes; import
them directly from their package. (3.0.0)

```python
from my_plugin import MyHook
```

## Operator extra links

The UI no longer executes custom link code. A custom `BaseOperatorLink`
declares an `xcom_key`; task code stores the complete URL in XCom under that
key, and task-detail views retrieve the URL through the XCom backend. (3.0.0)

## Dag and XCom representations

Dags are always JSON-serialized. Every custom object embedded in one must be
JSON-serializable. XCom pickling is also removed; use a custom XCom backend
when a value needs another representation. (3.0.0)

The API server no longer deserializes unknown Python objects simply to display
them; non-native XCom values use safer representations. The removed
`enable_xcom_deserialize_support` option cannot restore the old behavior.
`XCom.set()` and `XCom.get()` reject empty keys. (3.1.0)

## Versioned Task SDK serialization

The versioned Dag-serialization contract allows separately deployed Airflow
components to upgrade with less coordination. In the `3.1.0` batch it is a
decoupling foundation, not yet complete task/server code separation.

Use `airflow.sdk.serde` and `airflow.sdk.serde.serializers.*` instead of
`airflow.serialization.serde` and `airflow.serialization.serializers.*`. The
old imports warn and remain only until Airflow 4. (3.2.0)

## Custom deserializers

The `airflow.serialization.serializers` deserializer receives the loaded class
rather than a class-name string. Update custom signatures accordingly.
(3.1.0)

```python
def deserialize(cls: type, version: int, data: Any):
    ...
```

## Removed task-group serialization helpers

`get_task_group_children_getter` and `task_group_to_dict` are removed from
`airflow.sdk.definitions.taskgroup` and moved to server-side API services.
Application and plugin code must not import them. (3.1.0)

## Async and structured XCom

Async tasks can use asynchronous XCom accessors without blocking. Structured
outputs can round-trip as Pydantic model instances when output types are
registered from the worker-side Dag. (3.3.0)

## pandas DataFrame XCom rollout

Airflow recognizes both the pandas 2-era
`pandas.core.frame.DataFrame` name and pandas 3's `pandas.DataFrame` name.
Either pandas generation can therefore read values written by the other, but
only after every Airflow component has the updated serializer. Upgrade Airflow
everywhere, especially workers, before introducing pandas 3. (3.3.1)

An older Airflow cannot read pandas 3 DataFrame XComs;
`allowed_deserialization_classes` does not solve this, and rolling Airflow back
strands those XComs until it is upgraded again. The reader's pandas version
controls reconstructed dtypes: pandas 3 string columns use `str` rather than
`object`, and missing values use `nan` rather than `None`. Audit dtype branches,
identity comparisons, and `DataFrame.equals()` checks.

## Provider connection-form hooks

Provider hook methods `get_connection_form_widgets` and
`get_ui_field_behaviour` are deprecated. Do not build new provider UI behavior
on them. (3.2.0)

## Plugin hooks, navigation, and routes

`BaseTrigger.on_kill()` handles user actions against a trigger.
`task_instance_mutation_hook` receives the associated `DagRun`. Plugin
navigation can use `nav_top_level`, but `/auth` and `/pluginsv2` are reserved
prefixes. Owner-link and extra-link `href` values must be HTTP, HTTPS,
`mailto`, or relative URLs. (3.3.0)

React Apps and `iframe_views` are covered in
[APIs, CLI, and UI](api-cli-ui.md#react-apps-and-external-views).

# Deployment configuration

## Runtime and package support

### Python 3.14 installation

As of 1.93.0, package metadata permits Python 3.14 with an upper bound of
`<3.15`. Compatible releases of `redisvl`, `pypdf`, `openapi-core`, and the
native-bridge dependencies are included for this runtime.

### Admin UI build runtime

The 1.97.0 Admin UI toolchain targets Node.js 24. Its bootstrap flow selects
that dashboard version floor through nvm or fnm.

## Config source discovery

`CONFIG_FILE_PATH` starts `litellm` from a mounted configuration without a
`--config` argument. A bucket name and object key can load the file from S3;
set `LITELLM_CONFIG_BUCKET_TYPE=gcs` to use GCS instead.

```shell
CONFIG_FILE_PATH=/path/to/config.yaml

LITELLM_CONFIG_BUCKET_NAME=litellm-proxy
LITELLM_CONFIG_BUCKET_OBJECT_KEY=proxy-config.yaml
LITELLM_CONFIG_BUCKET_TYPE=gcs
```

## Shared named credentials

Top-level `credential_list` entries allow several deployments to use one
rotatable credential set through `litellm_credential_name`. Every entry needs
a `credential_info` mapping, even when it is empty.

```yaml
model_list:
  - model_name: chat
    litellm_params:
      model: azure/gpt-4o
      litellm_credential_name: azure-prod
credential_list:
  - credential_name: azure-prod
    credential_values:
      api_key: os.environ/AZURE_API_KEY
      api_base: os.environ/AZURE_API_BASE
    credential_info: {}
```

## Environment-scoped model exposure

Set `LITELLM_ENVIRONMENT` to `production`, `staging`, or `development`, then
list allowed environments in `model_info.supported_environments`.

```yaml
model_list:
  - model_name: chat
    litellm_params: {model: openai/gpt-4o}
    model_info:
      supported_environments: [production, staging]
```

## Per-model prompt framing

A Proxy model can override automatically detected prompt formatting under
`litellm_params`. The template supports initial and final text, per-role
`pre_message` and `post_message` strings, plus `bos_token` and `eos_token`.

```yaml
model_list:
  - model_name: custom-chat
    litellm_params:
      model: huggingface/example/instruct
      initial_prompt_value: "\n"
      roles:
        user: {pre_message: "<|im_start|>user\n", post_message: "<|im_end|>"}
        assistant: {pre_message: "<|im_start|>assistant\n", post_message: "<|im_end|>"}
      final_prompt_value: "\n"
```

## Custom token counting

Set `model_info.custom_tokenizer` to make `/utils/token_counter` use a chosen
Hugging Face tokenizer for the Proxy model. A private tokenizer may receive an
`auth_token`.

```yaml
model_info:
  custom_tokenizer:
    identifier: deepseek-ai/DeepSeek-V3-Base
    revision: main
    auth_token: os.environ/HUGGINGFACE_API_KEY
```

## Database topology and convergence

`DATABASE_URL_READ_REPLICA` sends read-only Prisma operations to a reader while
writes stay on `DATABASE_URL`. With `IAM_TOKEN_DB_AUTH=true`, LiteLLM refreshes
tokens for both connections.

`database_disable_prepared_statements` adds `pgbouncer=true`.
`database_extra_connection_params` takes precedence over that generated value.
Use `supported_db_objects` to limit which persisted object classes are loaded.
`proxy_config_reload_interval_seconds` controls cross-pod database refresh and
defaults to 30 seconds.

## Per-worker pools and timeout layers

`database_connection_pool_limit` applies to each worker. Compute total possible
connections as instances times workers times this value. The general database
call timeout is distinct from connection-open and idle/silent socket timeouts.

```yaml
general_settings:
  database_connection_pool_limit: 10
  database_connection_timeout: 60
  database_connect_timeout: 15
  database_socket_timeout: 300
```

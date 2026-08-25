# Assist, Voice, and AI

Use this reference for Assist pipelines, satellite conversations, speech, AI Tasks, and conversation providers. Entries are grouped by task; the parenthetical batch ID identifies when the guidance entered this patch.

## Assist, satellites, speech, and voice

### Assist and dashboard additions (2026.3)

Assist gains an intent for removing to-do items. Statistics graph cards can select a yearly period, the Security dashboard includes window covers, Sections views support sticky footer cards, and the Matter, Z-Wave, Zigbee, and Bluetooth settings pages have been reorganized.

### Assist Ask Question action (2025.7)

`assist_satellite.ask_question` lets an automation initiate a conversation, define expected sentence patterns for local Speech-to-Phrase recognition, and receive the matched answer ID and slots in a response variable. Optional `preannounce` and `preannounce_media_id` fields can precede the question.

```yaml
actions:
  - action: assist_satellite.ask_question
    data:
      entity_id: assist_satellite.living_room_voice_assistant
      question: "What kind of music do you want to listen to?"
      answers:
        - id: genre
          sentences: ["genre {genre}"]
    response_variable: answer
  - choose:
      - conditions: "{{ answer.id == 'genre' }}"
        sequence:
          - action: music_assistant.play_media
            data:
              media_id: "My {{ answer.slots.genre }} playlist"
              media_type: playlist
            target:
              entity_id: media_player.living_room_speakers
```

### Assist reasoning details (2026.4)

On the desktop web interface, each LLM-backed Assist response can expose a collapsible detail view containing thinking steps, tool calls, arguments, and results. The mobile companion apps do not yet show this view.

### Broadcast and thermostat voice intents (2025.2)

The Broadcast intent sends a spoken message to every other voice assistant, subject to language support. Voice commands can also set a thermostat target temperature, resolving the target by the speaker's area, its floor, or an explicitly named device.

### Cloud text-to-speech styles (2025.5)

Home Assistant Cloud text-to-speech adds voice variants and expressive styles such as friendly, angry, sad, and whisper, alongside many additional language and regional voices.

### Default Assist exposure (2025.1)

Voice Assistant settings now control whether newly created entities are exposed to Assist by default.

### Default voice-agent intents (2025.9)

The default non-LLM agent now uses fuzzy matching for English intent handling. Built-in intents can also change the volume of active media players and control fan speeds.

### Home Assistant Labs (2025.12)

**Settings > System > Labs** now contains optional preview features that are off by default and may change or disappear later. A feature can be enabled with an optional backup and disabled again without restarting Home Assistant.

### Home Assistant OS log-file removal (2025.11)

Home Assistant OS no longer duplicates Core logs into the configuration-folder log file. Logs remain viewable and downloadable under **Settings > System > Logs** and accessible through `ha core logs`.

### Music Assistant action responses (2025.1)

Music Assistant integration actions can now return response values for use by the calling automation or script.

### Streaming Assist chat (2025.3)

LLM-backed conversation agents now stream responses into Assist text chat. Commands can execute as soon as they arrive instead of waiting for the rest of the response to finish.

### Streaming Cloud text-to-speech (2025.8)

Home Assistant Cloud voices can now begin generating and playing speech before an entire response is available. This reduces the delay for long announcements and for voice responses produced by slower local AI models.

### Voice wake words and local confirmations (2025.10)

ESPHome-based voice assistants can assign two wake words, each to its own assistant, enabling per-language or local-versus-cloud routing on one satellite. For non-AI Assist agents, a command whose actions all affect the satellite's own area now produces a short beep instead of a spoken confirmation.

### Voice-controlled area cleaning (2026.4)

The `vacuum.clean_area` capability introduced in 2026.3 can now be invoked by voice, allowing a request such as cleaning a named room to use its mapped vacuum segments.

### YAML and template editor assistance (2026.5)

Home Assistant's code editors now provide context-aware YAML and Jinja autocomplete, including signatures and argument placeholders for template functions, filters, tests, and globals. ID arguments suggest matching entities, devices, areas, floors, or labels, while hover details show documentation and current entity or attribute values.

## Conversation agents and AI Tasks

### AI conversation diagnostics (2025.12)

The voice-assistant debug interface now shows an AI conversation's system prompt and tool calls, allowing its entity selection and actions to be audited from the voice-assistant configuration panel.

### AI Task image generation (2025.10)

Capable AI Task entities can use `ai_task.generate_image` with optional source-media attachments; the response variable exposes the generated asset through its `url` field.

```yaml
actions:
  - action: ai_task.generate_image
    data:
      task_name: Manga
      instructions: Transform this image into a cute manga.
      entity_id: ai_task.google_ai_task
      attachments:
        media_content_id: media-source://media_source/local/doorbell_test.png
        media_content_type: image/png
    response_variable: ai_image
# Generated asset path: {{ ai_image.url }}
```

### AI Task structured generation (2025.8)

An AI provider's AI Task sub-entry creates an entity for `ai_task.generate_data`, which can send files or camera images to the provider and return either text or selector-defined structured data to automations, scripts, and template entities.

```yaml
actions:
  - action: ai_task.generate_data
    data:
      task_name: Count chickens
      instructions: How many birds are inside the coop?
      structure:
        birds:
          selector:
            number:
      attachments:
        media_content_id: media-source://camera/camera.chicken_coop
        media_content_type: image/jpeg
    response_variable: result
# Structured output is available as result.data.birds
```

### Assist-satellite calls and conversations (2025.2)

An analog phone configured as an Assist satellite can be called with `assist_satellite.announce`. The new `assist_satellite.start_conversation` action lets an LLM-based agent call and begin a conversation with its first message; the default conversation agent cannot yet start this flow.

### Conversation and YAML integration options (2025.7)

Google Generative AI now defaults to Gemini 2.5 Flash and adds configurable text-to-speech with 30 voices across 24 languages. Ollama adds control of its `think` parameter, and Trend YAML configuration accepts unique IDs.

### Conversation-agent tools (2025.4)

The OpenAI conversation integration adds a content-generation action and optional web search, while the Google AI conversation integration also gains web search.

### Conversation-provider updates (2026.3)

OpenAI Conversation supports `gpt-image-1.5` for AI Task image generation. Anthropic supports Claude Opus 4.6 with adaptive thinking effort and provides native structured outputs on models 4.5 and newer.

### Default AI Task entity and suggestions (2025.8)

**Settings > System > General** can select a default AI Task entity, allowing `ai_task.generate_data` calls and shared blueprints to omit an entity. With a default selected and **AI suggestions** enabled, automation and script save dialogs can suggest names, descriptions, categories, and labels; using it sends the full automation or script plus other automation, script, and label names to the configured model.

### LLM voice conversation flow (2025.4)

Assist now detects when an LLM response contains a question and keeps listening for the answer without requiring the wake word again. LLM-backed conversations can also be started on ESPHome-based voice assistants, extending the earlier `assist_satellite.start_conversation` capability beyond analog phones.

### Model Context Protocol integrations (2025.2)

Home Assistant can act as both an MCP client, importing tools from MCP servers for conversation agents, and an MCP server, exposing Home Assistant context to external MCP clients.

## Intents and context

### Sentence-trigger context (2025.1)

Sentence triggers now receive the full conversation input, allowing their automations to use more than the matched sentence alone.

### Shopping-list completion intents (2025.7)

Shopping-list voice intents can now check off or mark list items complete.

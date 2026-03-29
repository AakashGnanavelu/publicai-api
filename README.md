publicai-api – Official Python Client
=====================================

Official Python client for the **Public AI Gateway**.
It wraps the HTTP API documented at `https://platform.publicai.co/docs` and
`https://platform.publicai.co/api`.

Features
--------

- **Typed sync and async clients**: `PublicAIClient` and `AsyncPublicAIClient`.
- **Environment-based configuration** for API key and user agent.
- **Convenience helpers** for returning the first chat message as a string.
- **Context manager support** (`with` / `async with`) for clean resource usage.
- **Friendly exceptions** (`PublicAIError` hierarchy).

Installation
------------
Find the latest download instructions on [TestPyPI](https://test.pypi.org/project/publicai-api/).

From PyPI:

```bash
pip install -i https://test.pypi.org/simple/ publicai-api
```

Install as `publicai-api`; in code you still import from `publicai`:

```python
from publicai import PublicAIClient, ChatMessage
```

For local development:

```bash
pip install -e .
```

Sync quickstart
---------------

```python
from publicai import PublicAIClient, ChatMessage

client = PublicAIClient(
    api_key="YOUR_API_KEY",       # or use PUBLICAI_API_KEY
    user_agent="MyApp/1.0",       # required by Public AI docs
)

# List models (GET /models)
models = client.list_models()
print(models)

# Simple chat completion – full response (POST /chat/completions)
response = client.chat_completions(
    model="swiss-ai/apertus-8b-instruct",
    messages=[
        ChatMessage(
            role="user",
            content="Hello! Can you help me understand open-source AI?",
        )
    ],
)
print(response)

# Convenience helper – just the first message content
text = client.chat(
    model="swiss-ai/apertus-8b-instruct",
    messages=[
        ChatMessage(role="user", content="Summarise open-source AI in 3 bullets.")
    ],
)
print(text)
```

Async quickstart
----------------

```python
import asyncio
from publicai import AsyncPublicAIClient, ChatMessage


async def main() -> None:
    async with AsyncPublicAIClient(
        api_key="YOUR_API_KEY",   # or use PUBLICAI_API_KEY
        user_agent="MyApp/1.0",
    ) as client:
        models = await client.list_models()
        print(models)

        text = await client.chat(
            model="swiss-ai/apertus-8b-instruct",
            messages=[ChatMessage(role="user", content="Say hi from async!")],
        )
        print(text)


asyncio.run(main())
```

Usage examples
--------------

### Using environment variables

```python
import os
from publicai import PublicAIClient, ChatMessage

# Set once (e.g. in .env or shell)
os.environ["PUBLICAI_API_KEY"] = "your-api-key"
os.environ["PUBLICAI_USER_AGENT"] = "MyApp/1.0"

client = PublicAIClient()
reply = client.chat(
    model="swiss-ai/apertus-8b-instruct",
    messages=[ChatMessage(role="user", content="What is the capital of France?")],
)
print(reply)
```

### Multi-turn conversation (system + user messages)

```python
from publicai import PublicAIClient, ChatMessage

client = PublicAIClient(api_key="YOUR_API_KEY", user_agent="MyApp/1.0")

messages = [
    ChatMessage(role="system", content="You are a helpful assistant that answers briefly."),
    ChatMessage(role="user", content="What is 2 + 2?"),
]
response = client.chat_completions(
    model="swiss-ai/apertus-8b-instruct",
    messages=messages,
)

# Append assistant reply for the next turn
assistant_content = response["choices"][0]["message"]["content"]
messages.append(ChatMessage(role="assistant", content=assistant_content))
messages.append(ChatMessage(role="user", content="And in hex?"))

reply = client.chat(model="swiss-ai/apertus-8b-instruct", messages=messages)
print(reply)
```

### Recommended model parameters

The [Public AI docs](https://platform.publicai.co/docs) recommend temperature 0.8, top_p 0.9, and up to 8192 output tokens:

```python
from publicai import PublicAIClient, ChatMessage

client = PublicAIClient(api_key="YOUR_API_KEY", user_agent="MyApp/1.0")

response = client.chat_completions(
    model="swiss-ai/apertus-8b-instruct",
    messages=[ChatMessage(role="user", content="Explain recursion in one paragraph.")],
    temperature=0.8,
    top_p=0.9,
    max_output_tokens=8192,
)
print(response["choices"][0]["message"]["content"])
```

### Parsing the full response (usage, role, etc.)

```python
from publicai import PublicAIClient, ChatMessage

client = PublicAIClient(api_key="YOUR_API_KEY", user_agent="MyApp/1.0")
response = client.chat_completions(
    model="swiss-ai/apertus-8b-instruct",
    messages=[ChatMessage(role="user", content="Say hello.")],
)

choice = response["choices"][0]
message = choice["message"]
print("Role:", message["role"])
print("Content:", message["content"])
print("Finish reason:", choice.get("finish_reason"))

if "usage" in response:
    usage = response["usage"]
    print("Prompt tokens:", usage.get("prompt_tokens"))
    print("Completion tokens:", usage.get("completion_tokens"))
```

### Listing available models

```python
from publicai import PublicAIClient

client = PublicAIClient(api_key="YOUR_API_KEY", user_agent="MyApp/1.0")
models_response = client.list_models()

for model in models_response.get("data", []):
    print(model.get("id", model))
```

### Error handling

```python
from publicai import (
    PublicAIClient,
    ChatMessage,
    PublicAIAuthenticationError,
    PublicAIAPIError,
)

try:
    client = PublicAIClient(user_agent="MyApp/1.0")
except PublicAIAuthenticationError as e:
    print("Missing API key:", e)
    exit(1)

try:
    text = client.chat(
        model="swiss-ai/apertus-8b-instruct",
        messages=[ChatMessage(role="user", content="Hi")],
    )
    print(text)
except PublicAIAPIError as e:
    print("API error:", e.status_code, e.payload)
```

### Using a context manager (sync)

```python
from publicai import PublicAIClient, ChatMessage

with PublicAIClient(api_key="YOUR_API_KEY", user_agent="MyApp/1.0") as client:
    models = client.list_models()
    text = client.chat(
        model="swiss-ai/apertus-8b-instruct",
        messages=[ChatMessage(role="user", content="Hello!")],
    )
print(text)
# Session is closed after the block
```

Environment Variables
---------------------

- **PUBLICAI_API_KEY**: If set, the clients can be constructed without
  passing `api_key` explicitly.
- **PUBLICAI_USER_AGENT**: Optional default user agent if you don’t want
  to provide `user_agent` in code. (If omitted, a library default is used.)

Endpoints Covered
-----------------

- **List Models**: `GET /models`
- **Chat Completions**: `POST /chat/completions`

These follow the official documentation: see
`https://platform.publicai.co/docs` and the API reference at
`https://platform.publicai.co/api`.

Error Handling
--------------

- **PublicAIError**: Base class for all library errors.
- **PublicAIAuthenticationError**: Raised when an API key is missing.
- **PublicAIAPIError**: Raised when the HTTP status is not 2xx. The exception
  includes the status code and any parsed JSON payload.
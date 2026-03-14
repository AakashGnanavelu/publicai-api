Public AI Python Client
=======================

Unofficial, featureful Python helper for the **Public AI Gateway**.
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

From PyPI (once published):

```bash
pip install publicai
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



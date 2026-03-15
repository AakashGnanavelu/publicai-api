"""
publicai-api – Official Public AI Python client.

Python client for the Public AI Gateway (https://platform.publicai.co/docs).
"""

from .client import (
    ChatMessage,
    PublicAIAPIError,
    PublicAIAuthenticationError,
    PublicAIClient,
    PublicAIError,
)
from .async_client import AsyncPublicAIClient
from .version import __version__

__all__ = [
    "PublicAIClient",
    "AsyncPublicAIClient",
    "PublicAIError",
    "PublicAIAuthenticationError",
    "PublicAIAPIError",
    "ChatMessage",
    "__version__",
]



"""
Public AI Python client.

Unofficial helper library for working with the
Public AI Gateway (`https://platform.publicai.co/docs`).
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



from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Common interface for AI language model providers."""

    @abstractmethod
    def generate_response(self, message: str) -> str:
        """Generate a response to a user message."""
        raise NotImplementedError

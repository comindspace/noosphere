from typing import Dict

from .configuration import Configuration

class OpenAIEmbeddingsConfiguration(Configuration):
    model: str
    headers: Dict[str, str]

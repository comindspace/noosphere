from typing import Dict

from configurations.configuration import *

class OpenAIEmbeddingsConfiguration(Configuration):
    model: str
    headers: Dict[str, str]

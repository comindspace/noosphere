from .configuration import Configuration

class ChatOpenAIConfiguration(Configuration):
    model: str
    openai_api_key: str

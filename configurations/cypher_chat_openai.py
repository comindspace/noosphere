from configurations.configuration import *

class CypherChatOpenAIConfiguration(Configuration):
    model: str
    openai_api_key: str
    temperature: float
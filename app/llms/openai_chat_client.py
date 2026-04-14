import importlib
from app.constants.app_constants import GPT_CHAT_MODEL
from langchain_openai import ChatOpenAI
from app.config.env_config import settings


class OpenAIChatClient:
  """Factory for Gemini chat model clients."""

  def __init__(self) -> None:
    """Initialize with model name and temperature from constants."""
    self.model_name = GPT_CHAT_MODEL.MODEL_NAME.value
    self.temprature = GPT_CHAT_MODEL.TEMPERATURE.value

  def create_client(self):
    """Create a Gemini chat model client.

    Returns:
      ChatGoogleGenerativeAI instance.
    """
    chat_client = ChatOpenAI(
      model = self.model_name,
      temperature = self.temprature,
      api_key=settings.OPENAI_API_KEY,
    )

    return chat_client
  
default_chat_client = OpenAIChatClient().create_client()
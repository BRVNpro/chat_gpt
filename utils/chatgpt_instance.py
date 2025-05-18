from utils.config import OPENAI_TOKEN, OPENAI_PROXY
from utils.chatgpt_service import ChatGptService

gpt = ChatGptService(token=OPENAI_TOKEN, proxy=OPENAI_PROXY)

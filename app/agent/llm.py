from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os
load_dotenv(encoding="utf-8")

llm = init_chat_model(
    model = "deepseek-v4-flash",
    model_provider="openai",
    base_url = "https://api.deepseek.com",
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    temperature = 0,
) 

# response = llm.invoke("你好")

# print(response.content)
import openai

from utils.config import OPENAI_TOKEN

openai.api_key = OPENAI_TOKEN


async def ask_chatgpt(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    try:
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=[
                {"role": "system", "content": "Ты дружелюбный и любознательный ассистент."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Ошибка при обращении к ChatGPT: {e}"

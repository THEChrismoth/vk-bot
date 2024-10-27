from httpx import AsyncClient
from openai import AsyncOpenAI
from config import GPT_key

# Создаем экземпляр клиента OpenAI с использованием прокси и базы данных
gpt = AsyncOpenAI(
    api_key=GPT_key,
    base_url="https://api.proxyapi.ru/openai/v1",
    http_client=AsyncClient(),
)


# Функция для получения ответов от модели GPT
async def gpt_request(prompt):
    response = await gpt.chat.completions.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": str(prompt)}]
    )
    return response


# Функция для получения изображений от модели GPT
async def gpt_image(prompt):
    response = await gpt.images.generate(
        prompt=prompt, n=1, size="1024x1024", model="dall-e-3"
    )
    return response

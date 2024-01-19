import aiohttp
import asyncio
import dotenv
import os

dotenv.load_dotenv()

server_url = 'http://' + os.getenv('SERVER_HOST_EN') + ":50055"


async def send_request(request):
    async with aiohttp.ClientSession() as session:
        async with session.post(server_url, json=request) as response:
            return await response.text()


async def main():
    request = {
        "knowledge_data": {
            "Кто ты?": "Олег",
            "Как дела?": "Хорошо"
        },
        "question": 'Как у вас дела?',
        "api_key": os.getenv('OPENAI_TOKEN'),
        "classification_error_message": 'Ошибка распознавания ;(',
        "detecting_error_message": "Ошибка Avatarex ;(",
    }

    response = await send_request(request)
    print("Response:", response)


# if __name__ == "__main__":
#    asyncio.run(main())

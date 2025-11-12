import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiohttp import ClientSession, ClientError

# Настраиваем логирование ошибок
logging.basicConfig(level=logging.INFO)

# Получаем токены из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Функция запуска бота
async def on_startup() -> None:
    logging.info("Бот запущен и готов к работе!")


# Функция остановки бота
async def on_shutdown() -> None:
    logging.info("Бот остановлен.")


# Обработчик команды /start
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    welcome_text = (
        f"Привет, {message.from_user.full_name}! 👋\n\n"
        "Я умный бот, который может общаться с тобой на любые темы. "
        "Задавай вопросы, обсуждай идеи или просто поболтай со мной!"
    )
    await message.answer(welcome_text)


# Обработчик команды /help
@dp.message(Command("help"))
async def command_help_handler(message: types.Message) -> None:
    help_text = (
        "📖 Помощь по использованию бота\n\n"
        "Я - бот, который может ответить на твои вопросы с помощью искусственного интеллекта. "
        "Вот что ты можешь сделать:\n\n"
        "• Напиши мне любое сообщение, и я постараюсь дать развернутый ответ\n"
        "• Используй команду /start, чтобы начать общение заново\n"
        "• Если у тебя есть вопросы или предложения, свяжись с разработчиком\n\n"
        "Просто напиши мне что-нибудь, и я помогу тебе!"
    )

    # Создаем кнопку для связи с разработчиком
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(
                text="💬 Написать разработчику",
                url="https://t.me/Arche006"
            )]
        ]
    )

    await message.answer(help_text, reply_markup=keyboard)


# Обработка текстовых сообщений
@dp.message(F.text)
async def message_handler(message: types.Message) -> None:
    user_message = message.text

    # Показываем статус "печатает"
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        # Формируем заголовки для запроса к OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        # Подготавливаем данные для запроса
        request_data = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {"role": "user", "content": user_message}
            ]
        }

        # Отправляем асинхронный запрос к API
        async with ClientSession() as session:
            async with session.post(OPENROUTER_API_URL, json=request_data, headers=headers) as response:
                api_response = await response.json()

                # Логируем успешный ответ от API
                logging.info("Успешный ответ от API получен")

        # Извлекаем текст ответа от модели
        bot_response = api_response['choices'][0]['message']['content'].strip()

    except Exception as e:
        # Логируем подробную информацию об ошибке
        logging.error(f"Ошибка при обращении к API: {e}", exc_info=True)
        bot_response = "Извините, произошла ошибка при обработке вашего запроса."

    # Отправляем ответ пользователю
    await message.answer(bot_response)


# Запуск приложения
if __name__ == '__main__':
    import asyncio

    # Регистрируем обработчики запуска и остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Запускаем бота
    asyncio.run(dp.start_polling(bot, skip_updates=True))
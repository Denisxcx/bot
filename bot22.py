import os
import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler,
                          CallbackContext, CallbackQueryHandler,
                          MessageHandler, filters)
import database

# Инициализация базы данных
database.init_db()

# 🔑 Укажи свой API-ключ OpenAI
OPENAI_API_KEY =
openai.api_key = OPENAI_API_KEY

# 🔑 Укажи свой токен Telegram бота
TOKEN =
chat_responses = [
    "Как дела? Мне всегда интересно, как вы проводите время! 😊",
    "Вы когда-нибудь задумывались, какой у вас идеальный партнер? 💭",
    "Расскажите немного о себе. Я вас слушаю! 🗣️",
    "Как насчет кофе и интересной беседы? ☕️",
    "Ваша улыбка освещает мой день! 🌞",
    "Что для вас значит любовь? ❤️"
]

async def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    database.add_user(user_id)

    keyboard = [
        [InlineKeyboardButton("Подписаться", callback_data='subscribe')],
        [InlineKeyboardButton("Отписаться", callback_data='unsubscribe')],
        [InlineKeyboardButton("Флирт", callback_data='flirt')],
        [InlineKeyboardButton("Общение", callback_data='chat')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if database.is_user_subscribed(user_id):
        await update.message.reply_text('Привет! Вы уже подписаны. Используйте меню для общения.', reply_markup=reply_markup)
    else:
        await update.message.reply_text('Привет! Я бот для флирта. Оформите подписку, чтобы получить доступ к дополнительному контенту:', reply_markup=reply_markup)

async def inline_button_handler(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатия на inline-кнопки"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == 'subscribe':
        await subscribe(query, user_id)
    elif query.data == 'unsubscribe':
        await unsubscribe(query, user_id)
    elif query.data == 'flirt':
        await flirt(query, user_id)
    elif query.data == 'chat':
        await chat(query, user_id)

async def subscribe(query, user_id):
    """Подписывает пользователя"""
    database.set_subscription(user_id, 1)
    await query.edit_message_text('Спасибо за подписку! Теперь вы можете начать флиртовать!')

async def unsubscribe(query, user_id):
    """Отписывает пользователя"""
    database.set_subscription(user_id, 0)
    await query.edit_message_text('Вы отписались от услуг. Надеюсь, увидим вас снова!')

async def flirt(query, user_id):
    """Отправляет сообщение с флиртом, если пользователь подписан"""
    if database.is_user_subscribed(user_id):
        await query.edit_message_text('Флиртуем! Что скажете о своём идеальном партнере?')
    else:
        await query.edit_message_text('Сначала оформите подписку, чтобы начать флирт!')

async def chat(query, user_id):
    """Общение с пользователем через AI"""
    if database.is_user_subscribed(user_id):
        await query.message.reply_text("Напишите мне что-нибудь, и я отвечу!")
        context.user_data["chat_mode"] = True  # Активируем режим чата
    else:
        await query.edit_message_text('Сначала оформите подписку, чтобы начать общение!')

async def handle_message(update: Update, context: CallbackContext):
    """Обработка текстовых сообщений"""
    user_id = update.effective_user.id
    if not database.is_user_subscribed(user_id):
        await update.message.reply_text("Чтобы начать диалог, подпишитесь!")
        return

    user_message = update.message.text
    bot_reply = await generate_ai_response(user_message)

    await update.message.reply_text(bot_reply)

async def generate_ai_response(user_input):
    """Generate a response from OpenAI API"""
    try:
        # Asynchronous call to OpenAI API to generate a response
        response = await openai.ChatCompletion.acreate(  # ⚡ Using async call
            model="gpt-4",  # Change the model if needed (replace gpt-4 with gpt-3.5-turbo or others)
            messages=[{"role": "user", "content": user_input}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        # Handle any errors from OpenAI API and provide a friendly error message
        return f"Ошибка в генерации ответа: {e}"

def main():
    """Запуск бота"""
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(inline_button_handler))

    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
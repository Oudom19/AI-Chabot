import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your Telegram Bot token
TELEGRAM_TOKEN = "7673859545:AAEzn8jl8536pFp0J8mdvpw2U41mdg0wcLk"

# Rasa server URL
RASA_API_URL = "http://localhost:5005/webhooks/rest/webhook"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_first_name = update.effective_user.first_name
    await update.message.reply_text(f'Hi {user_first_name}! Welcome to the ECI Bot. How can I assist you today?')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('I am the official virtual assistant of ECI, here to assist you in navigating the digital tools and services provided by the Store!')


def send_message_to_rasa(message_text, sender_id):
    """Send user message to Rasa and get response."""
    payload = {
        "sender": sender_id,
        "message": message_text
    }

    try:
        response = requests.post(RASA_API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with Rasa: {e}")
        return [{"text": "Sorry, I'm having trouble connecting to my brain right now. Please try again later."}]


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user message and get response from Rasa."""
    user_message = update.message.text
    user_id = str(update.effective_user.id)

    # Send message to Rasa
    rasa_responses = send_message_to_rasa(user_message, user_id)

    # Send Rasa's responses back to Telegram
    for response in rasa_responses:
        # Handle text responses
        if "text" in response:
            await update.message.reply_text(response["text"])

        # Handle image responses if your Rasa bot supports them
        if "image" in response:
            await update.message.reply_photo(response["image"])

        # You can add more response types (buttons, etc.) as needed


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Register message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Bot started. Press Ctrl+C to stop.")


if __name__ == '__main__':
    main()

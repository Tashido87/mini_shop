import asyncio
import json
import logging
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- Configuration ---
# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with the token you got from BotFather
BOT_TOKEN = '7231846645:AAGtYJawZZKUu3x4kgggsSFt3g71m9WalLM' 
# Your Chat ID to receive order notifications
CHAT_ID = 1871309877 

# --- Logging Setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Helper Function ---
def format_currency(price):
    """Formats a number as a currency string."""
    return f"{price:,.0f} MMK"

# --- Main Handler for Web App Data ---
async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles data received from the web app.
    """
    if not update.message or not update.message.web_app_data:
        return

    data = json.loads(update.message.web_app_data.data)
    user = update.effective_user
    
    logger.info(f"Received order from {user.first_name} (ID: {user.id}): {data}")

    # --- Format the order details into a nice message ---
    message_lines = [
        "🎉 New Order Received! 🎉\n",
        f"<b>From:</b> {user.first_name} (ID: <code>{user.id}</code>)\n",
        "<b><u>Order Details:</u></b>\n"
    ]
    
    total_price = 0
    if 'items' in data and data['items']:
        for name, details in data['items'].items():
            quantity = details.get('quantity', 0)
            price = details.get('price', 0)
            item_total = quantity * price
            total_price += item_total
            message_lines.append(f"  - {name} (x{quantity}) - {format_currency(item_total)}")
    
    message_lines.append(f"\n<b>Total Amount: {format_currency(total_price)}</b>")

    # --- Send the formatted message to your specified chat ID ---
    try:
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text="\n".join(message_lines),
            parse_mode='HTML'
        )
        logger.info(f"Order notification sent to chat ID {CHAT_ID}")

        # Optional: Send a confirmation message back to the user who placed the order
        await update.message.reply_text("Thank you! Your order has been received and is being processed.")

    except Exception as e:
        logger.error(f"Failed to send order notification: {e}")
        # Let the user know something went wrong
        await update.message.reply_text("Sorry, there was an error processing your order. Please contact support.")


# --- Main Bot Function ---
def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Add a handler for messages containing web_app_data
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))

    print("Bot is running... Press Ctrl-C to stop.")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

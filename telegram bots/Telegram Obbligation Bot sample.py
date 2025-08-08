import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import (Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes)
from telegram.constants import ChatMemberStatus
# Here's a telegram bot that checks if users are subscribed to a channel before allowing them to send messages in a group.
#it is also called as a obbligation bot, because it obliges users to subscribe to a channel before being able to write in a group.
# This bot will mute users who are not subscribed to the channel and provide them with a button to subscribe.
# It also allows users to verify their subscription status and unmute them if they are subscribed.
#this bot is designed to work with a specific channel and group, so you need to replace the API_TOKEN, CHANNEL_USERNAME, and ADMIN_ID with your own values.
#however it is written in italian, so you can change the messages to your preferred language.
# Make sure to install the required libraries using pip:
# pip install python-telegram-bot==20.0a2
# and to run the bot, you need to have a Telegram bot token, which you can get from the BotFather on Telegram.
#for any information or help, you can contact me on my discord: vitoos967


# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot API Token
API_TOKEN = "your_api_token_here"  # Replace with your bot's API token
CHANNEL_USERNAME = "your_channel_username"  # Replace with your channel username
ADMIN_ID = "123456789"  # Replace with your admin ID

# Check subscription status
async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        logger.info(f"Controllo iscrizione per user_id {user_id}: {member.status}")
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        logger.error(f"Errore nel controllo sottoscrizione per user_id {user_id}: {e}")
        return False

# Handle messages in groups
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Ignore messages from a channel (sent via sender_chat)
        if update.message.sender_chat:
            logger.info(f"Messaggio ignorato, inviato da un canale.")
            return
        
        logger.info(f"Ricevuto messaggio da @{user.username} nel gruppo {chat_id}")

        if not await check_subscription(user.id, context.bot): #se non è iscritto 
            # Mute the user
            logger.info(f"Mutando l'utente @{user.username} perché non iscritto al canale.")
            #comando per restringere il mittente  con l'id della chat, l'id dell'user e il permesso da modificare
            await context.bot.restrict_chat_member( 
                chat_id=chat_id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )

            # Notify the user with buttons
            reply_msg = await update.message.reply_text(
                f"Ciao @{user.username}, iscriviti al canale per poter scrivere nel gruppo!",
                reply_markup=InlineKeyboardMarkup([[ 
                    InlineKeyboardButton("Canale", url=f"https://t.me/{CHANNEL_USERNAME}"),
                    InlineKeyboardButton("Verifica", callback_data=f"verify_{user.id}_{update.message.message_id}")
                ]])
            )
            # Store the message sent by the bot
            bot_message_id = reply_msg.message_id  # Save bot's reply message ID
            #avvia il timer di 3 minuti per il messaggio
            context.application.job_queue.run_once(
            callback=verification_timeout,        
            when=180,                             
            data=(chat_id, user.id, reply_msg.message_id) )

        else:
            logger.info(f"L'utente @{user.username} è già iscritto al canale principale.")
    except Exception as e:
        logger.error(f"Errore nella gestione del messaggio: {e}")

# Verify user subscription
async def verify_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        #prende vari dati necessari per alcune funzioni da chi verifica
        query = update.callback_query
        data = query.data.split("_")
        user_id = int(data[1])
        message_id = int(data[2])
        chat_id = query.message.chat.id

        logger.info(f"Verifica iscrizione per user_id {user_id} nel gruppo {chat_id}")

        # Controllo se l'utente è iscritto al canale
        is_subscribed = await check_subscription(user_id, context.bot)
        
        if is_subscribed:
            # Unmute the user
            logger.info(f"L'utente user_id {user_id} è iscritto al canale, smutandolo.")
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_other_messages=True,
                    can_send_polls=True,
                     can_add_web_page_previews=True
                )
            )
            
            # Rimuovi solo il messaggio di verifica inviato dal bot
            bot_message_id = query.message.message_id  # Recupera l'ID del messaggio inviato dal bot
            await context.bot.delete_message(chat_id=chat_id, message_id=bot_message_id)

            await query.answer("Grazie per esserti iscritto! Ora puoi scrivere nel gruppo.")
        else:
            logger.info(f"L'utente user_id {user_id} non è iscritto al canale.")
            await query.answer("Non sei ancora iscritto! Assicurati di esserti iscritto correttamente.", show_alert=True)
    except Exception as e:
        logger.error(f"Errore nella verifica della sottoscrizione: {e}")

#funzione per cancellare il messaggio
async def verification_timeout(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id, user_id, msg_id = job.data

    try:
        # Prova a cancellare il messaggio se ancora ce
        await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
    except Exception:
        pass  # senò passa avanti

    # Controllo se l'utente si è sbloccato
    member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    if member.can_send_messages:
        # Se può già inviare, significa che si è iscritto e verificato in tempo:
        return
    # Altrimenti lo smuto
    await context.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(can_send_messages = True,
                    can_send_other_messages=True,
                    can_send_polls=True,
                     can_add_web_page_previews=True 
                    )
    )

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        username = user.username or "Anonimo"

        # Welcome message
        welcome_message = f"Hey @{username}, benvenuto/a nel bot!\n\n" \
                          f"Questo bot serve per monitorare se gli utenti sono iscritti al canale principale."

        # Button for main channel
        keyboard = [[InlineKeyboardButton("Canale principale", url=f"https://t.me/{CHANNEL_USERNAME}")],]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message:
            await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Errore nella funzione start: {e}")
        if update.message:
            await update.message.reply_text("Si è verificato un errore. Riprova più tardi.")

# Main function
def main():
    try:
        application = Application.builder().token(API_TOKEN).build()

        # Command handlers
        application.add_handler(CommandHandler("start", start))

        # Message handler for groups
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Callback handlers
        application.add_handler(CallbackQueryHandler(verify_subscription, pattern="^verify_"))

        # Start the bot
        application.run_polling()
    except Exception as e:
        logger.error(f"Errore nella funzione main: {e}")

if __name__ == "__main__":
    main()

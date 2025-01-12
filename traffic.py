from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import threading
import time
import random

MENU, ENTER_WEBSITE, TRAFFIC_RUNNING = range(3)

user_tokens = {}
admin_id = "7042632176"

def start(update, context):
    user_id = str(update.message.from_user.id)
    if user_id not in user_tokens:
        user_tokens[user_id] = 0
    update.message.reply_text(
        "Welcome! Please choose an option:\n"
        "1. Send Traffic (Deducts 1 Token)\n"
        "2. Check Tokens\n"
        "3. Stop Sending Traffic\n"
        "Reply with the number."
    )
    return MENU

# Function to handle menu choices
def menu_choice(update, context):
    user_id = str(update.message.from_user.id)
    choice = update.message.text
    if choice == "1":
        if user_tokens[user_id] > 0:
            update.message.reply_text("Enter the website URL where you want to send traffic:")
            return ENTER_WEBSITE
        else:
            update.message.reply_text("You don't have enough tokens. Contact the admin to get more.")
            return MENU
    elif choice == "2":
        update.message.reply_text(f"You have {user_tokens[user_id]} tokens.")
        return MENU
    elif choice == "3":
        context.user_data['stop_traffic'] = True
        update.message.reply_text("Traffic generation stopped.")
        return MENU
    else:
        update.message.reply_text("Invalid choice. Please try again.")
        return MENU

def enter_website(update, context):
    user_id = str(update.message.from_user.id)
    url = update.message.text
    context.user_data['website_url'] = url
    context.user_data['stop_traffic'] = False

    user_tokens[user_id] -= 1
    update.message.reply_text(f"Traffic will now be sent to {url}. You have {user_tokens[user_id]} tokens left. Type '3' to stop.")
    threading.Thread(target=send_traffic, args=(url, context)).start()
    return TRAFFIC_RUNNING

def send_traffic(url, context):
    while not context.user_data.get('stop_traffic', False):
        ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        print(f"Simulated visit to {url} from IP: {ip}")
        time.sleep(18)

def add_tokens(update, context):
    if str(update.message.from_user.id) != admin_id:
        update.message.reply_text("You are not authorized to perform this action.")
        return
    try:
        args = context.args
        user_id, tokens = args[0], int(args[1])
        if user_id in user_tokens:
            user_tokens[user_id] += tokens
            update.message.reply_text(f"Added {tokens} tokens to user {user_id}. They now have {user_tokens[user_id]} tokens.")
        else:
            update.message.reply_text("User ID not found.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /addtokens <user_id> <tokens>")

# Function for the admin to check user tokens
def check_tokens(update, context):
    if str(update.message.from_user.id) != admin_id:
        update.message.reply_text("You are not authorized to perform this action.")
        return
    try:
        user_id = context.args[0]
        if user_id in user_tokens:
            update.message.reply_text(f"User {user_id} has {user_tokens[user_id]} tokens.")
        else:
            update.message.reply_text("User ID not found.")
    except IndexError:
        update.message.reply_text("Usage: /checktokens <user_id>")

def main():
    API_TOKEN = "7530630999:AAEUs3GYK_hKybXw3yrSTaGHgjhLdmCHmJg"
    updater = Updater(API_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [MessageHandler(Filters.text & ~Filters.command, menu_choice)],
            ENTER_WEBSITE: [MessageHandler(Filters.text & ~Filters.command, enter_website)],
            TRAFFIC_RUNNING: [MessageHandler(Filters.text & ~Filters.command, menu_choice)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Admin-only commands
    dp.add_handler(CommandHandler('addtokens', add_tokens, pass_args=True))
    dp.add_handler(CommandHandler('checktokens', check_tokens, pass_args=True))

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

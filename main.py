import logging
import my_config as config
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(f"""Здравствуйте {user.mention_markdown_v2()}!""",
                              reply_markup=ForceReply(selective=True), )


def help_command(update: Update, context: CallbackContext):
    text = '\n'.join(commands.keys())
    update.message.reply_text(f'доступные команды \n {text}')


def echo(update: Update, context: CallbackContext):
    update.message.reply_text(f"Я получил сообщение {update.message.text}")


def main():
    uper = Updater(config.TOKEN)
    dispatcher = uper.dispatcher
    for i in commands.keys():
        dispatcher.add_handler(CommandHandler(i[1:], commands[i]))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    uper.start_polling()

    uper.idle()


commands = {'/start': start, '/help': help_command}
if __name__ == "__main__":
    main()

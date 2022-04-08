import logging
import my_config as config
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def task(context):
    """Выводит сообщение"""
    job = context.job
    context.bot.send_message(job.context, text='КУКУ!')


def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def unset(update, context):
    """Удаляет задачу, если пользователь передумал"""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    update.message.reply_text(text)


def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.message.chat_id
    try:
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Извините, не умеем возвращаться в прошлое')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(task, due, context=chat_id, name=str(chat_id))

        text = f'Вернусь через {due} секунд!'
        if job_removed:
            text += ' Старая задача удалена.'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Использование: /set <секунд>')


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(f"""Здравствуйте {user.mention_markdown_v2()}!""",
                              reply_markup=ForceReply(selective=True), )


def help_command(update: Update, context: CallbackContext):
    text = '\n'.join(commands.keys()) + '\n' + '\n'.join(spec_commands)
    update.message.reply_text(f'доступные команды \n {text}')


def echo(update: Update, context: CallbackContext):
    update.message.reply_text(f"Я получил сообщение {update.message.text}")


def time_now(update: Update, context: CallbackContext):
    now = datetime.now().time()
    hour = now.hour
    min = now.minute
    sec = now.second
    update.message.reply_text(f"час - {hour}, минута - {min}, секунда - {sec}")


def today_date(update: Update, context: CallbackContext):
    now = datetime.now().date()
    year = now.year
    month = now.month
    day = now.day
    update.message.reply_text(f"год - {year}, месяц - {month}, день - {day}")


def main():
    uper = Updater(config.TOKEN)
    dispatcher = uper.dispatcher
    for i in commands.keys():
        dispatcher.add_handler(CommandHandler(i[1:], commands[i]))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dispatcher.add_handler(CommandHandler("set", set_timer,
                                          pass_args=True,
                                          pass_job_queue=True,
                                          pass_chat_data=True))
    dispatcher.add_handler(CommandHandler("unset", unset,
                                          pass_chat_data=True)
                           )

    uper.start_polling()

    uper.idle()


commands = {'/start': start, '/help': help_command, '/time': time_now, '/date': today_date}
spec_commands = ['/set', '/unset']
if __name__ == "__main__":
    main()

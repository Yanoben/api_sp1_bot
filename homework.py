import os
import time
import requests
import telegram
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('logger.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)


def parse_homework_status(homework):
    homework_name = homework['lesson_name']
    homework_status = homework['status']
    if homework_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    homework_statuses = requests.get(url, headers=headers,
                                     params={'from_date': current_timestamp})
    if homework_statuses.status_code == 200:
        logging.info('Working')
    else:
        logging.error('Error')
        bot.send_message(CHAT_ID, 'Error server unavilable')
    homework = homework_statuses.json()
    return homework


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = 1621680882

    while True:
        try:
            homework = get_homeworks(current_timestamp)
            send_message(parse_homework_status(homework['homeworks'][0]))
            time.sleep(20 * 60)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()

import os
import time
import requests
import telegram
import logging
from dotenv import load_dotenv


load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    homework_statuses = {
        'approved': 'Ревьюеру всё понравилось, работа зачтена!',
        'reviewing': 'Проект пока на ревью.',
        'rejected': 'К сожалению, в работе нашлись ошибки.',
    }
    message = homework_statuses.get(homework_status)
    return (f'У вас проверили работу "{homework_name}"!\n\n{message}')


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
    try:
        homework = homework_statuses.json()
        return homework
    except Exception as e:
        message = f'Не удается преобразовать в json(), Oшибкa: {e}'
        logging.error(message)
        bot.send_message(CHAT_ID, message)


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    current_timestamp = 1621680882

    logging.basicConfig(
        level=logging.DEBUG,
        filename='main.log',
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
    )

    while True:
        try:
            homework = get_homeworks(current_timestamp)
            try:
                send_message(parse_homework_status(homework['homeworks'][0]))
            except Exception as e:
                message = f'Oшибкa: {e}'
                logging.error(message)
                send_message(message)
            time.sleep(60 * 60)

        except Exception as e:
            message = f'Бот упал с ошибкой: {e}'
            logging.error(message)
            send_message(message)
            time.sleep(5)


if __name__ == '__main__':
    main()

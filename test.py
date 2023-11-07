import time
import logging
import os
import psutil
import requests
from requests.exceptions import RequestException


# Настройка логирования
logging.basicConfig(filename='memory_monitor.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Порог использования памяти в процентах
MEMORY_THRESHOLD = int(os.getenv('MEMORY_THRESHOLD', 80))

# URL API для отправки тревоги
ALARM_URL = os.getenv('ALARM_URL', "http://example.com/api/alarm")

# Максимальное количество попыток отправки
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))

# Интервал между попытками (секунды)
RETRY_INTERVAL = int(os.getenv('RETRY_INTERVAL', 10))


def send_alarm(memory_usage):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(ALARM_URL, json={"alarm": f"Memory usage is high: {memory_usage}%"})
            if response.status_code == 200:
                logging.info("Alarm sent successfully!")
                return
            else:
                logging.warning(f"Failed to send alarm! Status code: {response.status_code}")
        except RequestException as e:
            logging.error(f"Exception occurred when sending alarm: {e}")

        time.sleep(RETRY_INTERVAL * (2 ** attempt))  # Exponential backoff


def check_memory_usage():
    memory_usage = psutil.virtual_memory().percent
    logging.info(f"Current memory usage is: {memory_usage}%")

    if memory_usage > MEMORY_THRESHOLD:
        logging.warning(f"Memory threshold exceeded: {memory_usage}%")
        send_alarm(memory_usage)


if __name__ == "__main__":
    check_memory_usage()

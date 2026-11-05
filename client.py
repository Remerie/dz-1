import socket
import struct
import sys
import time
import logging
from pathlib import Path

logging.basicConfig(
    filename=Path(__file__).with_name("client.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger("CLIENT")
logger.info("Клиент запущен")
COMMANDS = [
    "GET users",
    "GET users/user1",
    "GET users/user99",
    "POST users/user1/score:100",
    "POST users/user1/score100",
    "TEST 500",
    "TEST RESET",
    "DELETE users/user1",
]

DELAY_SECONDS = 1

def send_command(command):
    logger.info("Введена команда: %s", command)

    try:
        with socket.create_connection(("127.0.0.1", 8080), timeout=5) as client:
            if command == "TEST RESET":
                client.sendall(b"GET us")
                logger.info("Отправлены неполные данные: GET us")

                fmt = "hh" if sys.platform == "win32" else "ii"
                client.setsockopt(
                    socket.SOL_SOCKET,
                    socket.SO_LINGER,
                    struct.pack(fmt, 1, 0)
                )
            else:
                client.sendall(command.encode("utf-8"))
                logger.info("Команда отправлена: %s", command)

                client.shutdown(socket.SHUT_WR)
                response = client.makefile("r", encoding="utf-8").read()

        if command == "TEST RESET":
            logger.warning("Клиент принудительно сбросил TCP-соединение")
            print("Результат: соединение принудительно сброшено")
        else:
            logger.info("Получен ответ сервера: %s", response.strip())
            print("Ответ сервера:", response.strip())

        return True

    except OSError as error:
        logger.exception("Ошибка обмена с сервером: %s", error)
        print(f"Ошибка соединения: {error}")
        return False

def main():
        logger.info("Клиент запущен")
        print("Клиент запущен")

        for index, command in enumerate(COMMANDS, start=1):
            print(f"\n{'-' * 60}")
            print(f"Команда {index}/{len(COMMANDS)}: {command}")

            if not send_command(command):
                print("Отправка запросов остановлена.")
                break

            if index < len(COMMANDS):
                time.sleep(DELAY_SECONDS)
        else:
            print("\nSuccess!")

        logger.info("Клиент завершил работу")

if __name__ == "__main__":
        main()
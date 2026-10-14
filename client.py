import socket
import struct
import sys
import logging
from pathlib import Path

logging.basicConfig(
    filename=Path(__file__).with_name("interaction.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger("CLIENT")
logger.info("Клиент запущен")

while True:
    try:
        command = input("Введите команду: ")
    except (EOFError, KeyboardInterrupt):
        logger.info("Клиент завершил работу")
        break

    logger.info("Введена команда: %s", command)

    try:
        with socket.create_connection(("127.0.0.1", 8080)) as client:
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
            print("Соединение принудительно сброшено")
        else:
            logger.info("Получен ответ сервера: %s", response.strip())
            print(response.strip())

    except OSError as error:
        logger.exception("Ошибка обмена с сервером: %s", error)
        print(f"Ошибка соединения: {error}")
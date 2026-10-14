import socket
import json

USERS_DATA = {
    "user1": {"name": "Алексей", "game": "Dota 2", "level": 42, "score": 15320, "playtime_hours": 210},
    "user2": {"name": "Мария", "game": "Valorant", "level": 30, "score": 9870, "playtime_hours": 95},
    "user3": {"name": "Игорь", "game": "CS2", "level": 55, "score": 21000, "playtime_hours": 340}
}


def make_response(code, message, data=None, error=None):
    result = {
        "status_code": code,
        "message": message
    }

    if error is not None:
        result["error"] = error
    else:
        result["data"] = data

    return result


def process_command(command):

    if command == "GET users":
        return make_response(200, "OK", data=USERS_DATA)

    elif command.startswith("GET users/"):
        user_id = command.split("/", 1)[1]

        if not user_id or "/" in user_id:
            return make_response(400, "Bad Request",
                                 error="Неверный формат GET запроса")

        if user_id not in USERS_DATA:
            return make_response(404, "Not Found",
                                 error="Пользователь не найден")

        return make_response(200, "OK",
                             data=USERS_DATA[user_id])

    elif command.startswith("POST "):
        request = command[5:]

        path, separator, score = request.partition(":")
        path = path.strip()
        score = score.strip()

        if path.startswith("/"):
            path = path[1:]

        parts = path.split("/")

        if (not separator or len(parts) != 3
                or parts[0] != "users"
                or not parts[1]
                or parts[2] != "score"):
            return make_response(400, "Bad Request",
                                 error="Неверный формат POST запроса")

        user_id = parts[1]

        if not score.isascii() or not score.isdigit():
            return make_response(400, "Bad Request",
                                 error="Поле score должно содержать только цифры")

        if user_id not in USERS_DATA:
            return make_response(404, "Not Found",
                                 error="Пользователь не найден")

        try:
            points = int(score)
        except ValueError:
            return make_response(400, "Bad Request",
                                 error="Некорректное значение score")

        USERS_DATA[user_id]["score"] += points

        return make_response(200, "OK",
                             data=USERS_DATA[user_id])

    elif command.split(" ")[0] in ("PUT", "DELETE", "PATCH"):
        return make_response(405, "Method Not Allowed",
                             error="Метод не поддерживается")

    else:
        return make_response(400, "Bad Request",
                             error="Неизвестная или некорректная команда")


with socket.socket() as server:
    server.bind(("127.0.0.1", 8080))
    server.listen()
    print("Сервер запущен")

    while True:
        connection, address = server.accept()

        print(f"Клиент {address[0]}:{address[1]} подключился")

        with connection:
            try:
                command = connection.makefile(
                    mode="r",
                    encoding="utf-8"
                ).read().strip()

                print(f"Клиент {address[0]} отправил команду: {command}")

                if command == "TEST 500":
                    raise RuntimeError("Тестовая ошибка сервера")

                result = process_command(command)

            except ConnectionResetError as error:
                print(f"Клиент оборвал соединение: {error}")
                continue

            except Exception as error:
                print(f"Ошибка сервера: {error}")
                result = make_response(
                    500,
                    "Internal Server Error",
                    error="Внутренняя ошибка сервера"
                )

            response = json.dumps(result, ensure_ascii=False) + "\n"
            try:
                connection.sendall(response.encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError) as error:
                print(f"Не удалось отправить ответ клиенту: {error}")
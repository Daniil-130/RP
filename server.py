import asyncio
import aiohttp
from aiohttp import web

# Список для хранения всех подключенных клиентов
connected_clients = []

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Добавляем новое подключение в список
    connected_clients.append(ws)

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    # Обработка РП команд и сообщений
                    response = handle_rp_message(msg.data)

                    # Рассылаем сообщение всем подключенным клиентам
                    for client in connected_clients:
                        if client is not ws:
                            await client.send_str(response)
    finally:
        # Убираем клиента из списка при отключении
        connected_clients.remove(ws)

    return ws

def handle_rp_message(message):
    """
    Обрабатывает РП сообщения и команды.
    """
    if message.startswith('/roll'):
        # Пример команды /roll для броска кубика
        result = random.randint(1, 20)
        return f"Результат броска кубика: {result}"
    elif message.startswith('/me'):
        # Пример команды /me для описания действия
        action = message[4:]
        return f"* {action}"
    else:
        # Обычное сообщение чата
        return message

async def main():
    app = web.Application()
    app.add_routes([web.get('/', websocket_handler)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

    print("Сервер запущен на http://0.0.0.0:8080")

    # Оставляем сервер работать бесконечно
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())

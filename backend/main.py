from fastapi import FastAPI, WebSocket
from core.usb_monitor import monitor_usb_with_callback
import threading

app = FastAPI()

clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except:
        clients.remove(websocket)


async def broadcast(data):
    for client in clients:
        await client.send_json(data)


def start_usb_monitor():
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def callback(results):
        loop.run_until_complete(broadcast({
            "type": "usb_scan",
            "results": results
        }))

    monitor_usb_with_callback(callback)


@app.on_event("startup")
def startup():
    thread = threading.Thread(target=start_usb_monitor, daemon=True)
    thread.start()

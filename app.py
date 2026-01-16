#!/usr/bin/env python

import asyncio
import http
import os
import signal

import websockets
from websockets.asyncio.server import serve

# This will hold all active WebSocket connections
clients = set()

async def echo(websocket):
    # Register the new client
    clients.add(websocket)
    try:
        async for message in websocket:
            # Broadcast the message to all other connected clients
            for client in clients:
                if client != websocket:  # Don't send the message back to the sender
                    await client.send(message)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Unregister the client when disconnected
        clients.remove(websocket)

def health_check(connection, request):
    if request.path == "/healthz":
        return connection.respond(http.HTTPStatus.OK, "OK\n")

async def main():
    port = int(os.environ["PORT"])
    async with serve(echo, "", port, process_request=health_check, subprotocols=["permessage-deflate"],) as server:
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, server.close)
        await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())

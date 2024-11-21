import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from typing import Dict, List
from app.router import auth_router, chat_router, user_router, endereco_router, categoria_router, home_router
from app.models.chat import save_message, get_participants_in_chat

templates = Jinja2Templates(directory="app/views")

# Criação da aplicação FastAPI
app = FastAPI()

# Configuração de CORS (opcional, caso você precise habilitar o acesso de diferentes domínios)
origins = [
    "http://localhost",
    "http://localhost:8000",  # Front-end local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar a pasta de arquivos estáticos (CSS, JS, Imagens)
app.mount("/app/static", StaticFiles(directory="app/static"), name="static")

# Incluindo os controladores (rotas)
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(endereco_router.router)
app.include_router(categoria_router.router)
app.include_router(home_router.router)
app.include_router(chat_router.router)

# Dictionary to store active connections per chat_id
active_connections: Dict[int, List[WebSocket]] = {}

# Function to manage new connections
async def connect(websocket: WebSocket, chat_id: int):
    await websocket.accept()
    if chat_id not in active_connections:
        active_connections[chat_id] = []
    active_connections[chat_id].append(websocket)

# Function to handle disconnections
async def disconnect(websocket: WebSocket, chat_id: int):
    active_connections[chat_id].remove(websocket)
    if not active_connections[chat_id]:
        del active_connections[chat_id]

# Function to broadcast messages to all clients in a chat room
async def broadcast(chat_id: int, message: dict):
    if chat_id in active_connections:
        for connection in active_connections[chat_id]:
            await connection.send_json(message)

# WebSocket endpoint for chat
@app.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int):
    await connect(websocket, chat_id)
    try:
        while True:
            data = await websocket.receive_json()
            message = {
                "user_id": data["user_id"],
                "message": data["message"],
                "timestamp": data["timestamp"],
                "chat_id": chat_id
            }
            # Save the message to the database
            await save_message(chat_id, data["user_id"], data["message"])
            # Broadcast the message to all clients connected to this chat
            await broadcast(chat_id, message)
            
            # Notify other participants in the chat who are not currently in this chat
            participants = get_participants_in_chat(chat_id)
            for participant_id in participants:
                if participant_id != data["user_id"]:
                    if participant_id in active_user_connections:
                        # Here is where you include the notification_message
                        notification_message = {
                            "type": "new_message",
                            "chat_id": chat_id,
                            "message": {
                                "user_id": data["user_id"],
                                "message": data["message"],
                                "timestamp": data["timestamp"]
                            }
                        }
                        # Send the notification to all WebSocket connections of the participant
                        for user_ws in active_user_connections[participant_id]:
                            await user_ws.send_json(notification_message)
    except WebSocketDisconnect:
        await disconnect(websocket, chat_id)
        
active_user_connections: Dict[int, List[WebSocket]] = {}

@app.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: int):
    await websocket.accept()
    user_id = int(user_id)
    if user_id not in active_user_connections:
        active_user_connections[user_id] = []
    active_user_connections[user_id].append(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()  # You can handle incoming messages if needed
    except WebSocketDisconnect:
        active_user_connections[user_id].remove(websocket)
        if not active_user_connections[user_id]:
            del active_user_connections[user_id]

# Rota de teste para verificar se a aplicação está funcionando
@app.get("/")
async def root(request: Request):
    return RedirectResponse(url="/auth/login")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
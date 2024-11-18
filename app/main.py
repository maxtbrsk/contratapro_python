import json
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from typing import Dict, List
from app.models.database import Database
from app.router import auth_router, chat_router, user_router, endereco_router, categoria_router, home_router
from app.models.chat import save_message

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

# Dicionário para armazenar conexões ativas por usuário
user_connections: Dict[int, List[WebSocket]] = {}

# Function to manage new connections
async def connect(websocket: WebSocket, chat_id: int, user_id: int):
    await websocket.accept()
    # Gerenciar conexões por chat (já existente)
    if chat_id not in active_connections:
        active_connections[chat_id] = []
    active_connections[chat_id].append(websocket)

    # Gerenciar conexões por usuário (novo)
    if user_id not in user_connections:
        user_connections[user_id] = []
    user_connections[user_id].append(websocket)

# Function to handle disconnections
async def disconnect(websocket: WebSocket, chat_id: int, user_id: int):
    # Desconectar da lista por chat
    if chat_id in active_connections and websocket in active_connections[chat_id]:
        active_connections[chat_id].remove(websocket)
        if not active_connections[chat_id]:
            del active_connections[chat_id]
    # Desconectar da lista por usuário
    if user_id in user_connections and websocket in user_connections[user_id]:
        user_connections[user_id].remove(websocket)
        if not user_connections[user_id]:
            del user_connections[user_id]

# Function to broadcast messages to all clients in a chat room
async def broadcast(chat_id: int, message: dict):
    if chat_id in active_connections:
        for connection in active_connections[chat_id]:
            await connection.send_json(message)

# WebSocket endpoint for chat
@app.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int):
    # Obter o user_id dos parâmetros de consulta
    user_id = int(websocket.query_params["user_id"])
    await connect(websocket, chat_id, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            message = {
                "user_id": data["user_id"],
                "message": data["message"],
                "timestamp": data["timestamp"]
            }
            # Salvar mensagem no banco de dados
            await save_message(chat_id, data["user_id"], data["message"])
            # Transmitir mensagem para todos os clientes no chat
            await broadcast(chat_id, message)
            # Notificar o outro usuário envolvido na conversa
            await notify_user(chat_id, data["user_id"], message)
    except WebSocketDisconnect:
        await disconnect(websocket, chat_id, user_id)

# Rota de teste para verificar se a aplicação está funcionando
@app.get("/")
async def root(request: Request):
    return RedirectResponse(url="/auth/login")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

async def notify_user(chat_id: int, sender_id: int, message: dict):
    # Obter o ID do outro usuário na conversa
    db = Database()
    query = """
        SELECT cliente_id, prestador_id FROM conversas WHERE id = %s
    """
    db.execute(query, (chat_id,))
    conversa = db.cursor.fetchone()
    db.close()

    if conversa:
        # Determinar o destinatário
        recipient_id = conversa["prestador_id"] if sender_id == conversa["cliente_id"] else conversa["cliente_id"]

        # Enviar notificação se o usuário estiver conectado
        if recipient_id in user_connections:
            for connection in user_connections[recipient_id]:
                await connection.send_json({
                    "type": "new_message_notification",
                    "chat_id": chat_id,
                    "message": message
                })

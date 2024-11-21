from fastapi import APIRouter, Depends, Request, Form, File, UploadFile
from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse

from app.controllers.chat_controller import create_chat_controller, get_all_chats, get_chat
from app.controllers.user_controller import get_current_user_id
from app.models.chat import ChatManager, get_chat_by_id, get_chats_by_user_id, mark_messages_as_read

templates = Jinja2Templates(directory="app/views")

router = APIRouter()

load_dotenv()

@router.post("/chat/{user_id}")
async def chat(request: Request, user_id: int):
    return create_chat_controller(request, user_id)

@router.get("/chat")
async def chats(request: Request):
    return get_all_chats(request)

@router.get("/chat/{chat_id}")
async def get_chat(request: Request, chat_id: int):
    user_id = int(get_current_user_id(request))
    conversa = get_chat_by_id(chat_id, user_id)
    # Marcar mensagens como lidas
    mark_messages_as_read(chat_id, user_id)
    chat_manager = ChatManager()
    chats = chat_manager.get_chats(user_id)
    return templates.TemplateResponse("chat/one_chat.html", {"request": request, "conversa": conversa, "chats": chats, "user_id": user_id})

@router.get("/chats")
def get_chats(user_id: int, chat_manager: ChatManager = Depends()):
    return chat_manager.get_chats(user_id)

@router.post("/chats/{chat_id}/read")
def mark_as_read(request:Request, chat_id: int, chat_manager: ChatManager = Depends()):
    user_id = get_current_user_id(request)
    chat_manager.mark_messages_as_read(chat_id, user_id)
    return {"status": "success"}

@router.get("/api/chats")
async def api_get_chats(request: Request, chat_manager: ChatManager = Depends()):
    user_id = int(get_current_user_id(request))
    chats = chat_manager.get_chats(user_id)  # Use ChatManager to get ordered chats
    chats_list = [dict(chat) for chat in chats]
    return JSONResponse(content=chats_list)
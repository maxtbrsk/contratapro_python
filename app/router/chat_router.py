from fastapi import APIRouter, Request, Form, File, UploadFile
from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.controllers.chat_controller import create_chat_controller, get_all_chats, get_chat

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
async def chat(request: Request, chat_id: int):
    return get_chat(request, chat_id)


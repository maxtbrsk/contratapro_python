from fastapi import Request, HTTPException, Form
from fastapi.responses import JSONResponse, RedirectResponse
from passlib.hash import bcrypt
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv

from app.controllers.user_controller import get_current_user_id
from app.models.chat import create_chat, get_chat_by_id, get_chats_by_user_id

views = Jinja2Templates(directory="app/views")

load_dotenv()

SECRET_KEY = os.getenv("SECRET")
ALGORITHM = "HS256"

def create_chat_controller(request: Request, user_id: int):
    current_user = get_current_user_id(request)
    create_chat(current_user, user_id)
    return RedirectResponse(url=f"/chat/{user_id}", status_code=303)

def get_all_chats(request: Request):
    current_user = get_current_user_id(request)
    chats = get_chats_by_user_id(current_user)
    return views.TemplateResponse("chat/chat.html", {"request": request, "chats": chats})

def get_chat(request: Request, chat_id: int):
    current_user = int(get_current_user_id(request))
    conversa = get_chat_by_id(chat_id, current_user)
    print(conversa)
    chats = get_chats_by_user_id(current_user)
    return views.TemplateResponse("chat/one_chat.html", {"request": request, "chats": chats, "conversa": conversa, "user_id": current_user})
    
    
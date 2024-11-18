from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.models.user import home_top_eight, get_categoria_users, search_users
from app.models.categoria import get_all_categorias, get_categoria_by_id, verify_categoria
from app.controllers.user_controller import get_current_user_id

views = Jinja2Templates(directory="app/views")

router = APIRouter()

async def home_page(request: Request):
    users =  home_top_eight()
    print(users)
    categorias =  get_all_categorias()
    user_id = get_current_user_id(request)
    print(users)
    print(categorias)
    
    return views.TemplateResponse("home/home.html", {"request": request, "users": users, "categorias": categorias, "user_id": user_id})

def search_page(request: Request, b: str):
    user_id = get_current_user_id(request)
    users = search_users(b)
    return views.TemplateResponse("busca/busca.html", {"request": request, "users": users, "busca": b, "user_id": user_id})

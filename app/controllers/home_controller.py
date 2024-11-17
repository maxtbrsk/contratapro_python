from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.models.user import home_top_eight, get_categoria_users, search_users
from app.models.categoria import get_all_categorias, get_categoria_by_id, verify_categoria

views = Jinja2Templates(directory="app/views")

router = APIRouter()

async def home_page(request: Request):
    users = await home_top_eight()
    categorias = await get_all_categorias()
    
    print(users)
    print(categorias)
    
    return views.TemplateResponse("home/home.html", {"request": request, "users": users, "categorias": categorias})

async def categories_page(request: Request, id: int):
    if id:
        if await verify_categoria(id):
            users = await get_categoria_users(id)
            categoria = await get_categoria_by_id(id)
            return views.TemplateResponse("categoria/categoria.html", {"request": request, "users": users, "categoria": categoria})
    return "Categoria não encontrada"

def search_page(request: Request, b: str):
    users = search_users(b)
    return views.TemplateResponse("busca/busca.html", {"request": request, "users": users, "busca": b})

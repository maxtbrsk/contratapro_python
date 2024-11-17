from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.antigos.user_controller import get_current_user_id
from app.antigos.endereco_controller import get_enderecos_by_usuario
from app.models.user import home_top_eight,  get_categoria_users, search_users
from app.models.categoria import get_all_categorias, get_categoria_by_id, verify_categoria

templates = Jinja2Templates(directory="app/views")

router = APIRouter()

@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    users = home_top_eight()
    categorias = get_all_categorias()
    
    print(users)
    print(categorias)
    
    return templates.TemplateResponse("home/home.html", {"request": request, "users": users, "categorias": categorias})

@router.get("/categoria", response_class=HTMLResponse)
async def categories_page(request: Request, id:int):
    if id.is_integer():
        if id:
            if verify_categoria(id):
                users =  get_categoria_users(id)
                categoria = get_categoria_by_id(id)
                return templates.TemplateResponse("categoria/categoria.html", {"request": request, "users": users, "categoria": categoria})
            
    return "Categoria não encontrada"

@router.get ("/busca", response_class=HTMLResponse)
async def search_page(request: Request, b: str):
    users = search_users(b)
    return templates.TemplateResponse("busca/busca.html", {"request": request, "users": users, "busca": b})

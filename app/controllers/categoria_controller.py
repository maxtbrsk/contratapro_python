from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.models.categoria import get_all_categorias, get_categoria_by_id, verify_categoria 
from app.models.categoria import relate_user_to_categoria
from app.controllers.user_controller import get_current_user_id
from app.models.user import get_categoria_users


templates = Jinja2Templates(directory="app/views")

router = APIRouter()

# Rota pra relacionar um usuário a uma categoria existente
def add_prest_catg(request: Request, categorias: list):
    user_id = get_current_user_id(request)
    for categoria in categorias:
        relate_user_to_categoria(prestador_id=user_id, categoria_id=categoria)
        print(categoria)
    return RedirectResponse(url="/home", status_code=303)

def categories_page(request: Request, id:int):
    if id.is_integer():
        if id:
            if verify_categoria(id):
                users =  get_categoria_users(id)
                categoria = get_categoria_by_id(id)
                return templates.TemplateResponse("categoria/categoria.html", {"request": request, "users": users, "categoria": categoria})
from typing import List
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from app.controllers.categoria_controller import categories_page
from app.controllers.categoria_controller import add_prest_catg
from app.models.categoria import get_all_categorias 
from app.models.categoria import relate_user_to_categoria
from app.controllers.user_controller import get_current_user_id

router = APIRouter()

# Rota pra relacionar um usuário a uma categoria existente
@router.post("/categorias")
async def add_prest_catg_route(request: Request, categorias: List[int] = Form(...)):
    user_id = get_current_user_id(request)
    for categoria in categorias:
        relate_user_to_categoria(prestador_id=user_id, categoria_id=categoria)
    return add_prest_catg(request, categorias)

@router.get("/categoria", response_class=HTMLResponse)
async def categories_page_route(request: Request, id: int):
    return categories_page(request, id)

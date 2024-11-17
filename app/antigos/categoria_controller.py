from fastapi import APIRouter, Form, HTTPException, Request
from app.models.categoria import get_all_categorias 
from app.models.categoria import relate_user_to_categoria
from app.antigos.user_controller import get_current_user_id

router = APIRouter()

# Rota pra relacionar um usuário a uma categoria existente
@router.post("/categorias")
async def add_prestador_categoria(request: Request, categorias: list = Form(..., alias="categorias[]")):
    user_id = get_current_user_id(request)
    for categoria in categorias:
        relate_user_to_categoria(prestador_id=user_id, categoria_id=categoria)
        print(categoria)
    return {"message": "Usuário relacionado às categorias com sucesso"}

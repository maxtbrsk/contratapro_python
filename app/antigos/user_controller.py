from fastapi import APIRouter, Request, HTTPException, Depends, Form
from app.models.user import get_user_by_telefone, update_user
from jose import jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET")
ALGORITHM = "HS256"

router = APIRouter()

# Função pra obter o ID do usuário autenticado a partir do token JWT
def get_current_user_id(request: Request):
    user_id = request.cookies.get("access_token")    
    return user_id

# Rota pra obter os dados do usuário logado
@router.get("/usuarios/me")
async def get_current_user(request: Request):
    user_id = get_current_user_id(request)
    user = get_user_by_telefone(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Retorna os dados do usuário sem a senha
    user.pop("senha", None)
    return user

# Rota para atualizar os dados do usuário logado
@router.put("/usuarios/me")
async def update_current_user(
    request: Request,
    nome_completo: str = Form(...),
    senha: str = Form(...),
    foto: str = Form(...)
):
    user_id = get_current_user_id(request)

    # Atualiza os dados do usuário
    update_user(
        user_id=user_id,
        nome_completo=nome_completo,
        senha=senha,
        foto=foto
    )

    return {"message": "Dados do usuário atualizados com sucesso"}


from fastapi import APIRouter, Request, HTTPException, Depends, Form
from app.models.user import get_user_by_telefone, update_user
from jose import jwt
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.models.user import get_user_by_id
from passlib.hash import bcrypt
templates = Jinja2Templates(directory="app/views")

load_dotenv()

SECRET_KEY = os.getenv("SECRET")
ALGORITHM = "HS256"

router = APIRouter()

# Função pra obter o ID do usuário autenticado a partir do token JWT
def get_current_user_id(request: Request):
    user_id = request.cookies.get("access_token")    
    return user_id

def get_current_user(request: Request):
    user_id = get_current_user_id(request)
    user = get_user_by_telefone(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Retorna os dados do usuário sem a senha
    user.pop("senha", None)
    return user


def update_current_user(
    request: Request,
    nome_completo: str,
    senha: str,
    foto: str
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

async def update_user_profile(
    request: Request,
    user_id: int,
    nome_completo: str = None,
    telefone: str = None,
    senha: str = None,
    tipo: str = None,
    area_atuacao: str = None,
    descricao: str = None,
    foto: bytes = None,
    foto_filename: str = None,
    curriculo: bytes = None,
    curriculo_filename: str = None
):
    current_user_id = get_current_user_id(request)
    if int(current_user_id) != user_id:
        raise HTTPException(status_code=403, detail="Não autorizado")

    update_data = {}
    if nome_completo: update_data['nome_completo'] = nome_completo
    if telefone: update_data['telefone'] = telefone
    if senha: update_data['senha'] = bcrypt.hash(senha)
    if tipo: update_data['tipo'] = tipo
    if area_atuacao: update_data['area_atuacao'] = area_atuacao
    if descricao: update_data['descricao'] = descricao

    if foto and foto_filename:
        update_data['foto'] = foto
        update_data['foto_filename'] = foto_filename

    if curriculo and curriculo_filename:
        update_data['curriculo'] = curriculo
        update_data['curriculo_filename'] = curriculo_filename

    if update_data:  # Only update if there's data to update
        from app.models.user import update_user_full
        await update_user_full(user_id, **update_data)
    
    return "Dados atualizados com sucesso"

def user_profile(request: Request, user_id: int):
    current_user = get_current_user_id(request)
    id = user_id
    user = get_user_by_id(id)
    if int(id) == int(current_user):
        return templates.TemplateResponse("user/my_profile.html", {"request": request, "user": user})
    if not user:
        return templates.TemplateResponse("user/non_existing.html", {"request": request})
    return templates.TemplateResponse("user/profile.html", {"request": request, "user": user})
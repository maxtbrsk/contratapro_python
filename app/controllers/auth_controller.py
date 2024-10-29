from fastapi import APIRouter, Request, HTTPException, Depends, Form
from fastapi.responses import JSONResponse, RedirectResponse
from app.models.user import create_user, get_user_by_telefone
from passlib.hash import bcrypt
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET")
ALGORITHM = "HS256"

router = APIRouter()

# Rota para registro de novo usuário
@router.post("/auth/register")
async def register_user(
    nome_completo: str = Form(...),
    telefone: str = Form(...),
    senha: str = Form(...),
    cpf: str = Form(...),
    tipo: str = Form(...),
    cnpj: str = Form(...),
    area_atuacao: str = Form(...),
    descricao: str = Form(...),
    curriculo: str = Form(...),
    foto: str = Form(...),
):
    # Verifica se o telefone já ta registrado
    if get_user_by_telefone(telefone):
        raise HTTPException(status_code=400, detail="Telefone já registrado")
    
    # Criptografa a senha do usuário
    hashed_password = bcrypt.hash(senha)
    
    # Cria o usuário
    user_id = create_user(
        nome_completo=nome_completo,
        telefone=telefone,
        senha=hashed_password,
        cpf=cpf,
        tipo=tipo,
        cnpj=cnpj,
        area_atuacao=area_atuacao,
        descricao=descricao,
        curriculo=curriculo,
        foto=foto
    )
    # Exemplo de chamada pra registro
    response = RedirectResponse(url="/criar_endereco", status_code=303)
    response.set_cookie(key="access_token", value=user_id, httponly=True)
    return response

# Rota pra login
@router.post("/auth/login")
async def login_user(
    telefone: str = Form(...),
    senha: str = Form(...)
):
    # Verifica se o usuário existe
    user = get_user_by_telefone(telefone)
    if not user or not bcrypt.verify(senha, user["senha"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    # Gera o token JWT
    
    response = JSONResponse({"message": "Login realizado com sucesso"})
    response.set_cookie(key="access_token", value=user['id'] , httponly=True)
    
    return response

# Rota para logout
@router.post("/auth/logout")
async def logout_user():
    response = JSONResponse({"message": "Logout realizado com sucesso"})
    response.delete_cookie(key="access_token")
    return response

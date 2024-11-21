from fastapi import Request, HTTPException, Form
from fastapi.responses import JSONResponse, RedirectResponse
from app.models.user import create_user, get_user_by_cnpj, get_user_by_cpf, get_user_by_telefone
from app.models.categoria import get_all_categorias
from passlib.hash import bcrypt
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv

views = Jinja2Templates(directory="app/views")

load_dotenv()

SECRET_KEY = os.getenv("SECRET")
ALGORITHM = "HS256"

async def register_user(
    request: Request,
    nome_completo: str,
    telefone: str,
    senha: str,
    cpf: str,
    tipo: str,
    cnpj: str,
    area_atuacao: str,
    descricao: str,
    foto: bytes,
    foto_filename: str,
    curriculo: bytes,
    curriculo_filename: str = None,
):
    if get_user_by_telefone(telefone):
        raise HTTPException(status_code=400, detail="Telefone já registrado")
    
    hashed_password = bcrypt.hash(senha)
    
    user_id = await create_user(
        nome_completo=nome_completo,
        telefone=telefone,
        senha=hashed_password,
        cpf=cpf,
        tipo=tipo,
        cnpj=cnpj,
        area_atuacao=area_atuacao,
        descricao=descricao,
        curriculo=curriculo,
        curriculo_filename=curriculo_filename,
        foto=foto,
        foto_filename=foto_filename
    )
    
    response = RedirectResponse(url="/criar_endereco", status_code=303)
    response.set_cookie(key="access_token", value=user_id, httponly=True)
    return response

def login_user(
    request: Request,
    telefone: str = Form(...),
    senha: str = Form(...)
):
    user = get_user_by_telefone(telefone)
    if not user or not bcrypt.verify(senha, user["senha"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    response = RedirectResponse(url="/home", status_code=303)
    response.set_cookie(key="access_token", value=user['id'], httponly=True)
    
    return response

def logout_user(request: Request):
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response


def register_page(request: Request):
    return views.TemplateResponse("auth/register_prestador.html", {"request": request})

def register_cliente_page(request: Request):
    return views.TemplateResponse("auth/register_cliente.html", {"request": request})

def login_page(request: Request):
    return views.TemplateResponse("auth/login.html", {"request": request})

def categorias_select(request: Request):
    categorias = get_all_categorias()
    print (categorias)
    return views.TemplateResponse("auth/categorias.html", {"request": request, "categorias": categorias})

def enderecos_page(request: Request):
    return views.TemplateResponse("auth/enderecos.html", {"request": request})

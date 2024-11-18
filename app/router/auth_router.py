from fastapi import APIRouter, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from app.controllers.auth_controller import register_cliente_page, register_user, login_user, logout_user, register_page, login_page, categorias_page, enderecos_page
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.post("/auth/register")
async def register_route(
    request: Request,
    nome_completo: str = Form(...),
    telefone: str = Form(...),
    senha: str = Form(...),
    cpf: str = Form(...),
    tipo: str = Form(...),
    cnpj: str = Form(None),
    area_atuacao: str = Form(None),
    descricao: str = Form(None),
    curriculo: UploadFile = File(None),
    foto: UploadFile = File(...)):
    curriculo_bytes = await curriculo.read() if curriculo else None
    curriculo_filename = curriculo.filename if curriculo else None
    foto_bytes = await foto.read()
    return await register_user(request, nome_completo, telefone, senha, cpf, tipo, cnpj, area_atuacao, descricao, foto_bytes, foto.filename, curriculo_bytes, curriculo_filename)

@router.post("/auth/login")
async def login_route(
    request: Request,
    telefone: str = Form(...),
    senha: str = Form(...)):
    return login_user(request, telefone, senha)

@router.get("/auth/logout")
async def logout_route(request: Request):
    return logout_user(request)

@router.get("/auth/register/prestador", response_class=HTMLResponse)
async def register_route(request: Request):
    if request.cookies.get("access_token"):
            return RedirectResponse(url="/home")
    return register_page(request)

@router.get("/auth/register/cliente", response_class=HTMLResponse)
async def register_route(request: Request):
    if request.cookies.get("access_token"):
            return RedirectResponse(url="/home")
    return register_cliente_page(request)

@router.get("/auth/login", response_class=HTMLResponse)
async def login_route(request: Request):
    if request.cookies.get("access_token"):
            return RedirectResponse(url="/home")
    return login_page(request)

@router.get("/categorias", response_class=HTMLResponse)
async def categorias_route(request: Request):
    return categorias_page(request)

@router.get("/criar_endereco", response_class=HTMLResponse)
async def enderecos_route(request: Request):
    return enderecos_page(request)


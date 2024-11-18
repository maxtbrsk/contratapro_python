from fastapi import APIRouter, Request, Form, File, UploadFile, HTTPException
from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.controllers.user_controller import update_user_profile, user_profile
from app.models.user import add_favorite, remove_favorite, get_favorites, get_user_by_id

templates = Jinja2Templates(directory="app/views")

router = APIRouter()

load_dotenv()

# View para a página do perfil do usuário
@router.get("/usuarios/{user_id}")
async def dynamic_profile_route(request: Request, user_id: int):
    return user_profile(request, user_id)

@router.post("/usuarios/update/{user_id}")
async def update_user_route(
    request: Request,
    user_id: int,
    nome_completo: str = Form(None),
    telefone: str = Form(None),
    senha: str = Form(None),
    tipo: str = Form(None),
    area_atuacao: str = Form(None),
    descricao: str = Form(None),
    foto: UploadFile = File(None),
    curriculo: UploadFile = File(None)
):
    foto_data = None
    foto_filename = None
    curriculo_data = None
    curriculo_filename = None

    if foto:
        foto_data = await foto.read()
        foto_filename = foto.filename

    if curriculo:
        curriculo_data = await curriculo.read()
        curriculo_filename = curriculo.filename
        
    ok = await update_user_profile(
        request,
        user_id,
        nome_completo,
        telefone,
        senha,
        tipo,
        area_atuacao,
        descricao,
        foto_data,
        foto_filename,
        curriculo_data,
        curriculo_filename
    )
    print(ok)
    return RedirectResponse(url=f"/usuarios/{user_id}", status_code=303)

@router.post("/favoritar/{prestador_id}")
def favoritar_usuario(request: Request, prestador_id: int):
    cliente_id = request.cookies.get("access_token")
    if not cliente_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    add_favorite(cliente_id, prestador_id)
    return RedirectResponse(url=f"/usuarios/perfil/{prestador_id}", status_code=303)

@router.post("/desfavoritar/{prestador_id}")
def desfavoritar_usuario(request: Request, prestador_id: int):
    cliente_id = request.cookies.get("access_token")
    if not cliente_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    remove_favorite(cliente_id, prestador_id)
    return RedirectResponse(url=f"/usuarios/perfil/{prestador_id}", status_code=303)

@router.get("/favoritos")
def ver_favoritos(request: Request):
    cliente_id = request.cookies.get("access_token")
    if not cliente_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    favoritos = get_favorites(cliente_id)
    return templates.TemplateResponse("user/favorites.html", {"request": request, "favoritos": favoritos})

@router.get("/usuarios/perfil/{user_id}")
def perfil_usuario(request: Request, user_id: int):
    usuario = get_user_by_id(user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    cliente_id = request.cookies.get("access_token")
    favoritos = get_favorites(cliente_id) if cliente_id else []
    favoritos_ids = [fav['id'] for fav in favoritos]
    
    return templates.TemplateResponse("user/profile.html", {
        "request": request,
        "user": usuario,
        "favoritos_ids": favoritos_ids
    })

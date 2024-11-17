from fastapi import APIRouter, Request, Form, File, UploadFile
from app.antigos.user_views import user_profile
from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.controllers.user_controller import update_user_profile, user_profile
from app.models.user import get_user_by_id
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
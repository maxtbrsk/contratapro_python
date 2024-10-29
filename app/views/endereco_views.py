from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.controllers.user_controller import get_current_user_id
from app.controllers.endereco_controller import get_enderecos_by_usuario

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# View para listar os endereços do usuário logado
@router.get("/criar_endereco", response_class=HTMLResponse)
async def enderecos_page(request: Request):
    return templates.TemplateResponse("endereco/enderecos.html", {"request": request})

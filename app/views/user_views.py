from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.controllers.user_controller import get_current_user_id
from app.models.user import get_user_by_id
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# View para a página do perfil do usuário
@router.get("/usuarios/perfil", response_class=HTMLResponse)
async def user_profile(request: Request):
    user_id = get_current_user_id(request)
    user = get_user_by_id(user_id)
    return templates.TemplateResponse("user/profile.html", {"request": request, "user": user})

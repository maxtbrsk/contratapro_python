from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.models.categoria import get_all_categorias

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# View para listar categorias
@router.get("/categorias", response_class=HTMLResponse)
async def categorias_page(request: Request):
    return templates.TemplateResponse("categoria/categorias.html", {"request": request})

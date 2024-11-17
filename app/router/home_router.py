from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.controllers.home_controller import home_page, search_page


router = APIRouter()

@router.get("/home", response_class=HTMLResponse)
async def home_page_route(request: Request):    
    return await home_page(request)

@router.get ("/busca", response_class=HTMLResponse)
async def search_page_route(request: Request, b: str):
    return search_page(request, b)

from fastapi import APIRouter, Request, Form

from app.controllers.endereco_controller import add_endereco

router = APIRouter()

# Rota pra adicionar um novo endereço pra o usuário logado
@router.post("/enderecos")
async def add_endereco_route(
    request: Request,
    rua: str = Form(...),
    numero: str = Form(...),
    bairro: str = Form(...),
    cidade: str = Form(...),
    estado: str = Form(...),
    cep: str = Form(...),
    complemento: str = Form(...)
):
    
    return add_endereco( request, rua, numero, bairro, cidade, estado, cep, complemento)

# Rota pra listar todos os endereços do usuário logado

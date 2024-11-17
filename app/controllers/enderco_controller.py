from fastapi import APIRouter, Request, Form
from app.models.endereco import create_endereco
from app.antigos.user_controller import get_current_user_id
from fastapi.responses import RedirectResponse
from app.models.user import get_user_type

router = APIRouter()

# Rota pra adicionar um novo endereço pra o usuário logado
def add_endereco(
    request: Request,
    rua: str,
    numero: str,
    bairro: str,
    cidade: str,
    estado: str,
    cep: str,
    complemento: str
):
    user_id = get_current_user_id(request)

    create_endereco(
        usuario_id=user_id,
        rua=rua,
        numero=numero,
        bairro=bairro,
        cidade=cidade,
        estado=estado,
        cep=cep,
        complemento=complemento
    )
    user_tipo=get_user_type(user_id)
    if user_tipo == "cliente":
        return RedirectResponse(url="/home", status_code=303)
    
    return RedirectResponse(url="/categorias", status_code=303)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import auth_controller, user_controller, endereco_controller, categoria_controller
from app.views import user_views, endereco_views, categorias_views, auth_views, home_views

# Criação da aplicação FastAPI
app = FastAPI()

# Configuração de CORS (opcional, caso você precise habilitar o acesso de diferentes domínios)
origins = [
    "http://localhost",
    "http://localhost:8000",  # Front-end local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar a pasta de arquivos estáticos (CSS, JS, Imagens)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Incluindo os controladores (rotas)
app.include_router(auth_controller.router)
app.include_router(user_controller.router)
app.include_router(endereco_controller.router)
app.include_router(categoria_controller.router)
app.include_router(user_views.router)
app.include_router(endereco_views.router)
app.include_router(categorias_views.router)
app.include_router(auth_views.router)
app.include_router(home_views.router)

# Rota de teste para verificar se a aplicação está funcionando
@app.get("/")
async def root():
    return {"message": "Bem-vindo à aplicação de busca de prestadores de serviço!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

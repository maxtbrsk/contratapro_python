import os, re


import bcrypt
from app.models.database import Database

def sanitize_filename(filename):
        return re.sub(r'[^a-zA-Z0-9&%$]', '', filename)

async def create_user(nome_completo, telefone, senha, cpf, tipo, cnpj=None, area_atuacao=None, descricao=None, curriculo=None, curriculo_filename=None, foto=None, foto_filename=None):
    curriculo_dir = "app/static/curriculos/"
    foto_dir = "app/static/fotos/"
    os.makedirs(curriculo_dir, exist_ok=True)
    os.makedirs(foto_dir, exist_ok=True)
    
    if not cnpj:
        cnpj = None
        
    foto_tipo = os.path.splitext(foto_filename)[1] if foto_filename else ''
    
    foto_hash = bcrypt.hashpw(sanitize_filename(foto_filename).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    foto_hash = sanitize_filename(foto_hash) + foto_tipo if foto_filename else None
    
    if curriculo and curriculo_filename:
        curriculo_hash = bcrypt.hashpw(sanitize_filename(curriculo_filename).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        curriculo_hash = sanitize_filename(curriculo_hash) + ".pdf"
        with open(os.path.join(curriculo_dir, curriculo_hash), "wb") as f:
            f.write(curriculo)
    else:
        curriculo_hash = None
    
    if foto and foto_filename:
        with open(os.path.join(foto_dir, foto_hash), "wb") as f:
            f.write(foto)
    else:
        foto_hash = None
    
    db = Database()
    query = """
        INSERT INTO usuarios (nome_completo, telefone, senha, cpf, tipo, cnpj, area_atuacao, descricao, curriculo, foto)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    db.execute(query, (nome_completo, telefone, senha, cpf, tipo, cnpj, area_atuacao, descricao, curriculo_hash, foto_hash))
    db.commit()
    
    query = "SELECT id FROM usuarios WHERE telefone = %s ORDER BY id DESC LIMIT 1"
    db.execute(query, (telefone,))
    result = db.cursor.fetchone()
    db.close()
    return result['id'] if result else None

def get_user_by_telefone(telefone):
    db = Database()
    query = "SELECT * FROM usuarios WHERE telefone = %s"
    db.execute(query, (telefone,))
    user = db.cursor.fetchone()
    db.close()
    return user

def get_user_by_cpf(cpf):
    db = Database()
    query = "SELECT * FROM usuarios WHERE cpf = %s"
    db.execute(query, (cpf,))
    user = db.cursor.fetchone()
    db.close()
    return user

def get_user_by_cnpj(cnpj):
    db = Database()
    query = "SELECT * FROM usuarios WHERE cnpj = %s"
    db.execute(query, (cnpj,))
    user = db.cursor.fetchone()
    db.close()
    return user

def get_user_by_id(user_id):
    db = Database()
    query = "SELECT * FROM usuarios WHERE id = %s"
    db.execute(query, (user_id,))
    user = db.cursor.fetchone()
    
    if user:
        query = """
            SELECT 
            c.nome AS categoria_nome,
            pc.categoria_id AS categoria_id
            FROM 
            prestador_categorias pc
            JOIN 
            categorias c ON pc.categoria_id = c.id
            WHERE 
            pc.prestador_id = %s;
        """
        db.execute(query, (user_id,))
        categorias = db.cursor.fetchall()
        user["categorias"] = categorias
        
        query = "SELECT * FROM enderecos WHERE usuario_id = %s"
        db.execute(query, (user_id,))
        endereco = db.cursor.fetchone()
        user["endereco"] = endereco
        
        query = "SELECT AVG(nota) AS media_avaliacao FROM avaliacoes WHERE prestador_id = %s"
        db.execute(query, (user_id,))
        avaliacao = db.cursor.fetchone()
        user["media_avaliacao"] = round(avaliacao["media_avaliacao"], 1) if avaliacao and avaliacao["media_avaliacao"] is not None else 0.0
    print(user)
    db.close()
    return user

def update_user(user_id, nome_completo=None, senha=None, foto=None):
    db = Database()
    fields_to_update = []
    params = []
    
    if nome_completo:
        fields_to_update.append("nome_completo = %s")
        params.append(nome_completo)
    
    if senha:
        fields_to_update.append("senha = %s")
        params.append(senha)

    if foto:
        fields_to_update.append("foto = %s")
        params.append(foto)

    if fields_to_update:
        query = f"UPDATE usuarios SET {', '.join(fields_to_update)} WHERE id = %s"
        params.append(user_id)
        db.execute(query, params)
        db.commit()

    db.close()

async def update_user_full(user_id, **kwargs):
    db = Database()
    fields_to_update = []
    params = []
    
    curriculo_dir = "app/static/curriculos/"
    foto_dir = "app/static/fotos/"
    os.makedirs(curriculo_dir, exist_ok=True)
    os.makedirs(foto_dir, exist_ok=True)
    
    if 'foto' in kwargs and 'foto_filename' in kwargs:
        foto = kwargs['foto']
        foto_filename = kwargs['foto_filename']
        foto_tipo = os.path.splitext(foto_filename)[1]
        foto_hash = bcrypt.hashpw(foto_filename.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        foto_hash += foto_tipo
        
        with open(os.path.join(foto_dir, foto_hash), "wb") as f:
            f.write(foto)
        
        fields_to_update.append("foto = %s")
        params.append(foto_hash)
        del kwargs['foto']
        del kwargs['foto_filename']
    
    if 'curriculo' in kwargs and 'curriculo_filename' in kwargs:
        curriculo = kwargs['curriculo']
        curriculo_filename = kwargs['curriculo_filename']
        curriculo_hash = bcrypt.hashpw(curriculo_filename.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        curriculo_hash += ".pdf"
        
        with open(os.path.join(curriculo_dir, curriculo_hash), "wb") as f:
            f.write(curriculo)
        
        fields_to_update.append("curriculo = %s")
        params.append(curriculo_hash)
        del kwargs['curriculo']
        del kwargs['curriculo_filename']

    # Handle remaining fields
    for key, value in kwargs.items():
        if value is not None and key not in ['cpf', 'cnpj']:
            fields_to_update.append(f"{key} = %s")
            params.append(value)

    if fields_to_update:
        query = f"UPDATE usuarios SET {', '.join(fields_to_update)} WHERE id = %s"
        params.append(user_id)
        db.execute(query, params)
        db.commit()

    db.close()

def get_user_type(user_id):
    db = Database()
    query = "SELECT tipo FROM usuarios WHERE id = %s"
    db.execute(query, (user_id,))
    user = db.cursor.fetchone()
    db.close()
    return user['tipo']

def home_top_eight():
    db = Database()
    query = """SELECT 
                    u.id AS prestador_id,
                    u.nome_completo, u.foto,
                    ROUND(COALESCE(AVG(a.nota), 0), 1) AS media_avaliacao
                FROM 
                    usuarios u
                LEFT JOIN 
                    avaliacoes a ON u.id = a.prestador_id
                WHERE 
                    u.tipo = 'prestador'
                GROUP BY 
                    u.id, u.nome_completo
                ORDER BY 
                    media_avaliacao DESC
                LIMIT 8;
                """
                
    db.execute(query)
    users = db.cursor.fetchall()
    
    query = """
            SELECT 
            c.nome AS categoria_nome,
            pc.categoria_id AS categoria_id
            FROM 
            prestador_categorias pc
            JOIN 
            categorias c ON pc.categoria_id = c.id
            WHERE 
            pc.prestador_id = %s;
            """
    
    for user in users:
        db.execute(query, (user["prestador_id"],))
        categorias = db.cursor.fetchall()
        user["categorias"] = categorias
    
    return users

def get_categoria_users(id):
    db = Database()
    query = """SELECT 
            pc.prestador_id
        FROM 
            prestador_categorias pc
        WHERE 
            pc.categoria_id = %s;"""
    db.execute(query, (id,))
    users_id = db.cursor.fetchall()
    users = []

    for user_id in users_id:
        query = """
            SELECT 
            u.*, 
            ROUND(COALESCE(AVG(a.nota), 0), 1) AS media_avaliacao
            FROM 
            usuarios u
            LEFT JOIN 
            avaliacoes a ON u.id = a.prestador_id
            WHERE 
            u.id = %s
            GROUP BY 
            u.id;
        """
        db.execute(query, (user_id["prestador_id"],))
        user = db.cursor.fetchone()
        query = """
            SELECT 
            c.nome AS categoria_nome,
            pc.categoria_id AS categoria_id
            FROM 
            prestador_categorias pc
            JOIN 
            categorias c ON pc.categoria_id = c.id
            WHERE 
            pc.prestador_id = %s;
        """
        db.execute(query, (user_id["prestador_id"],))
        categorias = db.cursor.fetchall()
        user["categorias"] = categorias
        users.append(user)
    
    print(users)
    return users
        
def search_users(term):
    db = Database()
    term = f"%{term}%"
    query = """
        SELECT DISTINCT u.id, u.nome_completo, u.area_atuacao, u.descricao, u.foto,
        ROUND(COALESCE(AVG(a.nota), 0), 1) AS media_avaliacao
        FROM usuarios u
        LEFT JOIN prestador_categorias pc ON u.id = pc.prestador_id
        LEFT JOIN categorias c ON pc.categoria_id = c.id
        LEFT JOIN avaliacoes a ON u.id = a.prestador_id
        WHERE u.nome_completo LIKE %s
        OR u.area_atuacao LIKE %s
        OR u.descricao LIKE %s
        OR c.nome LIKE %s
        GROUP BY u.id, u.nome_completo, u.area_atuacao, u.descricao
        ORDER BY media_avaliacao DESC
        LIMIT 20
        """
    db.execute(query, (term, term, term, term))
    users = db.cursor.fetchall()
        
    for user in users:
        query = """
            SELECT 
            c.nome AS categoria_nome,
            pc.categoria_id AS categoria_id
            FROM 
            prestador_categorias pc
            JOIN 
            categorias c ON pc.categoria_id = c.id
            WHERE 
            pc.prestador_id = %s;
            """
        db.execute(query, (user["id"],))
        categorias = db.cursor.fetchall()
        user["categorias"] = categorias
        
    db.close()
    return users

def add_favorite(cliente_id, prestador_id):
    from app.models.database import Database
    db = Database()
    query = "INSERT INTO favoritos (cliente_id, prestador_id) VALUES (%s, %s)"
    db.execute(query, (cliente_id, prestador_id))
    db.commit()
    db.close()

def remove_favorite(cliente_id, prestador_id):
    from app.models.database import Database
    db = Database()
    query = "DELETE FROM favoritos WHERE cliente_id = %s AND prestador_id = %s"
    db.execute(query, (cliente_id, prestador_id))
    db.commit()
    db.close()

def get_favorites(cliente_id: int):
    from app.models.database import Database
    db = Database()
    query = """
        SELECT f.*, u.nome_completo, u.foto FROM favoritos f
        JOIN usuarios u ON f.prestador_id = u.id
        WHERE f.cliente_id = %s
    """
    db.execute(query, (cliente_id,))
    favoritos = db.cursor.fetchall()
    print(favoritos)
    db.close()
    return favoritos

def add_evaluation(cliente_id, prestador_id, nota):
    db = Database()
    query = "SELECT * FROM avaliacoes WHERE cliente_id = %s AND prestador_id = %s"
    db.execute(query, (cliente_id, prestador_id))
    avaliacao = db.cursor.fetchone()
    
    if avaliacao:
        query = "UPDATE avaliacoes SET nota = %s WHERE cliente_id = %s AND prestador_id = %s"
        db.execute(query, (nota, cliente_id, prestador_id))
    else:
        query = "INSERT INTO avaliacoes (cliente_id, prestador_id, nota) VALUES (%s, %s, %s)"
        db.execute(query, (cliente_id, prestador_id, nota))
    
    db.commit()
    db.close()
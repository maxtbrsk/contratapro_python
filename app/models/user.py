from app.models.database import Database

def create_user(nome_completo, telefone, senha, cpf, tipo, cnpj=None, area_atuacao=None, descricao=None, curriculo=None, foto=None):
    db = Database()
    query = """
        INSERT INTO usuarios (nome_completo, telefone, senha, cpf, tipo, cnpj, area_atuacao, descricao, curriculo, foto)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    db.execute(query, (nome_completo, telefone, senha, cpf, tipo, cnpj, area_atuacao, descricao, curriculo, foto))
    db.commit()
    
    # Fetch the user ID after insertion
    query = "SELECT id FROM usuarios WHERE telefone = %s ORDER BY id DESC LIMIT 1"
    db.execute(query, (telefone,))
    result = db.cursor.fetchone()
    user_id = result['id']
    
    db.close()
    return user_id  # Optionally return the user ID if needed

def get_user_by_telefone(telefone):
    db = Database()
    query = "SELECT * FROM usuarios WHERE telefone = %s"
    db.execute(query, (telefone,))
    user = db.cursor.fetchone()
    db.close()
    return user

def get_user_by_id(user_id):
    db = Database()
    query = "SELECT * FROM usuarios WHERE id = %s"
    db.execute(query, (user_id,))
    user = db.cursor.fetchone()
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

def get_user_type (user_id):
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
                    u.nome_completo,
                COALESCE(AVG(a.nota), 0) AS media_avaliacao
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
        db.execute(query,(user["prestador_id"],))
        categorias = db.cursor.fetchall()
        user["categorias"] = categorias
    
    return users

def get_categoria_users(id):
    db =Database()
    query = """SELECT 
            pc.prestador_id
        FROM 
            prestador_categorias pc
        WHERE 
            pc.categoria_id = %s;"""
    db.execute(query,(id,))
    users_id = db.cursor.fetchall()
    users = []

    for user_id in users_id:
        query = """SELECT * FROM usuarios WHERE id = %s;"""
        db.execute(query,(user_id["prestador_id"],))
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
        db.execute(query,(user_id["prestador_id"],))
        categorias = db.cursor.fetchall()
        user["categorias"] = categorias
        users.append(user)
    
    print(users)
    return users

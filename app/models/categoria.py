from app.models.database import Database

def relate_user_to_categoria(prestador_id, categoria_id):
    db = Database()
    query = "INSERT INTO prestador_categorias (prestador_id, categoria_id) VALUES (%s, %s)"
    db.execute(query, (prestador_id, categoria_id))
    db.commit()
    db.close()

def get_all_categorias():
    db = Database()
    query = "SELECT * FROM categorias"
    db.execute(query)
    categorias = db.cursor.fetchall()
    return categorias

def verify_categoria(id):
    db= Database()
    query = "SELECT * FROM categorias WHERE id = %s"
    db.execute(query, (id,))
    categoria_id = db.cursor.fetchone()
    if categoria_id:
        return True
    return False

def get_categoria_by_id(id):
    db = Database()
    query = "SELECT nome, foto FROM categorias WHERE id = %s"
    db.execute(query, (id,))
    categoria = db.cursor.fetchone()
    return categoria
    
    
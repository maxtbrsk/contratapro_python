from app.models.database import Database

def create_chat(cliente_id, prestador_id):
    db = Database()
    query = "SELECT * FROM conversas WHERE cliente_id = %s AND prestador_id = %s"
    db.execute(query, (cliente_id, prestador_id))
    conversa = db.cursor.fetchone()
    print(conversa)
    if conversa:
        return False
    query = "INSERT INTO conversas (cliente_id, prestador_id) VALUES (%s, %s)"
    db.execute(query, (cliente_id, prestador_id))
    db.commit()
    db.close()
    return True



def get_chats_by_user_id(user_id):
        db = Database()
        query = """
            SELECT c.*, 
                CASE 
                    WHEN c.cliente_id = %s THEN p.nome_completo
                    ELSE cl.nome_completo
                END as outro_usuario_nome,
                CASE 
                    WHEN c.cliente_id = %s THEN p.foto
                    ELSE cl.foto
                END as outro_usuario_foto
            FROM conversas c
            JOIN usuarios cl ON c.cliente_id = cl.id
            JOIN usuarios p ON c.prestador_id = p.id
            WHERE c.cliente_id = %s OR c.prestador_id = %s
        """
        db.execute(query, (user_id, user_id, user_id, user_id))
        conversas = db.cursor.fetchall()
        db.close()
        return conversas

def get_chat_by_id(chat_id, user_id):
    db = Database()
    query = """
        SELECT c.*, 
            CASE 
                WHEN c.cliente_id = %s THEN p.nome_completo
                ELSE cl.nome_completo
            END as outro_usuario_nome,
            CASE 
                WHEN c.cliente_id = %s THEN p.foto
                ELSE cl.foto
            END as outro_usuario_foto
        FROM conversas c
        JOIN usuarios cl ON c.cliente_id = cl.id
        JOIN usuarios p ON c.prestador_id = p.id
        WHERE c.id = %s AND (c.cliente_id = %s OR c.prestador_id = %s)
    """
    db.execute(query, (user_id, user_id, chat_id, user_id, user_id))
    conversa = db.cursor.fetchone()
    query_mensagens = """
        SELECT m.*, u.nome_completo, u.foto
        FROM mensagens m
        JOIN usuarios u ON m.usuario_id = u.id
        WHERE m.conversa_id = %s
        ORDER BY m.data_envio ASC
    """
    db.execute(query_mensagens, (chat_id,))
    mensagens = db.cursor.fetchall()
    for mensagem in mensagens:
        mensagem['usuario_id'] = int(mensagem['usuario_id'])
    conversa['mensagens'] = mensagens
    db.close()
    return conversa
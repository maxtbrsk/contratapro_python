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
            END as outro_usuario_foto,
            (
                SELECT mensagem FROM mensagens 
                WHERE conversa_id = c.id 
                ORDER BY data_envio DESC 
                LIMIT 1
            ) as ultima_mensagem,
            (
                SELECT COUNT(*) FROM mensagens 
                WHERE conversa_id = c.id AND usuario_id != %s AND lida = FALSE
            ) as nao_lidas
        FROM conversas c
        JOIN usuarios cl ON c.cliente_id = cl.id
        JOIN usuarios p ON c.prestador_id = p.id
        WHERE c.cliente_id = %s OR c.prestador_id = %s
    """
    db.execute(query, (user_id, user_id, user_id, user_id, user_id))
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

# app/models/chat.py

async def save_message(chat_id, user_id, content):
    db = Database()
    query = """
        INSERT INTO mensagens (conversa_id, usuario_id, mensagem, data_envio, lida)
        VALUES (%s, %s, %s, NOW(), FALSE)
    """
    db.execute(query, (chat_id, user_id, content))
    db.commit()
    db.close()

def mark_messages_as_read(chat_id, user_id):
    db = Database()
    query = """
        UPDATE mensagens 
        SET lida = TRUE 
        WHERE conversa_id = %s AND usuario_id != %s AND lida = FALSE
    """
    db.execute(query, (chat_id, user_id))
    db.commit()
    db.close()
from app.models.database import Database

def create_endereco(usuario_id, rua, numero, bairro, cidade, estado, cep=None, complemento=None):
    db = Database()
    query = """
        INSERT INTO enderecos (usuario_id, rua, numero, bairro, cidade, estado, cep)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    db.execute(query, (usuario_id, rua, numero, bairro, cidade, estado, cep))
    db.commit()
    db.close()

def get_enderecos_by_usuario(usuario_id):
    db = Database()
    query = "SELECT * FROM enderecos WHERE usuario_id = %s"
    db.execute(query, (usuario_id,))
    enderecos = db.cursor.fetchall()
    db.close()
    return enderecos

def update_endereco(endereco_id, rua=None, numero=None, bairro=None, cidade=None, estado=None, cep=None, complemento=None):
    db = Database()
    fields_to_update = []
    params = []
    
    if rua:
        fields_to_update.append("rua = %s")
        params.append(rua)
    
    if numero:
        fields_to_update.append("numero = %s")
        params.append(numero)
    
    if bairro:
        fields_to_update.append("bairro = %s")
        params.append(bairro)
    
    if cidade:
        fields_to_update.append("cidade = %s")
        params.append(cidade)
    
    if estado:
        fields_to_update.append("estado = %s")
        params.append(estado)
    
    if cep:
        fields_to_update.append("cep = %s")
        params.append(cep)
    
    if fields_to_update:
        query = f"UPDATE enderecos SET {', '.join(fields_to_update)} WHERE id = %s"
        params.append(endereco_id)
        db.execute(query, params)
        db.commit()

    db.close()

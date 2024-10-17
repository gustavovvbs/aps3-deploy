from flask import Blueprint, request
from bson.objectid import ObjectId
from . import mongo


users_bp = Blueprint('users', __name__, url_prefix='/usuarios')

@users_bp.route('/', methods=['GET'])
def get_all_users():
    users = mongo.db.usuarios.find()
    users_list = []
    for user in users:
        user['_id'] = str(user['_id'])
        users_list.append(user)
    resp = {"usuarios": users_list}
    return resp, 200

@users_bp.route('/<id_usuario>', methods=['GET'])
def get_user(id_usuario):
    dados_usuario = mongo.db.usuarios.find_one({'_id': ObjectId(id_usuario)}, {"_id": 0})
    if dados_usuario is None:
        return {'erro': 'Usuário não encontrado'}, 404
    resp = {"usuario": dict(dados_usuario)}
    return resp, 200

@users_bp.route('/', methods=['POST'])
def post_user():
    data = request.json
    campos = ['nome', 'data_nascimento', 'cpf']

    for campo in campos:
        valor = data.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            return {"erro": f"O campo {campo} deve ser uma string não vazia"}, 400

    if mongo.db.usuarios.find_one({"cpf": data.get("cpf")}):
        return {"erro": "CPF já existe"}, 400

    result = mongo.db.usuarios.insert_one(data)
    return {"id": str(result.inserted_id)}, 201

@users_bp.route('/<id_usuario>', methods=['DELETE'])
def delete_user(id_usuario):
    mongo.db.emprestimos.delete_many({'id_usuario': id_usuario})

    result = mongo.db.usuarios.delete_one({'_id': ObjectId(id_usuario)})
    if result.deleted_count == 0:
        return {'erro': "Usuário não encontrado"}, 404

    return {"mensagem": 'Usuário deletado'}, 200

@users_bp.route('/<id_usuario>', methods=['PUT'])
def put_user(id_usuario):
    data = request.json
    dados_obrigatorios = ["nome", 'cpf', 'data_nascimento']

    for campo in dados_obrigatorios:
        if campo not in data:
            return {"erro": f"{campo} é obrigatório"}, 400

    new_data = {'$set': data}
    result = mongo.db.usuarios.update_one({'_id': ObjectId(id_usuario)}, new_data)

    if result.matched_count == 0:
        return {'erro': "Usuário não encontrado"}, 404

    return {"mensagem": 'Usuário atualizado'}, 200
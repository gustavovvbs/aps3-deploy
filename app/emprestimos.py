from flask import Blueprint, request
from bson.objectid import ObjectId
from . import mongo
from datetime import datetime, timedelta

emprestimos_bp = Blueprint('emprestimos', __name__, url_prefix='/emprestimos')

@emprestimos_bp.route('/', methods=['GET'])
def get_all_emprestimos():
    filtro = {}
    dados_emprestimos = mongo.db.emprestimos.find(filtro)
    emprestimos_list = []
    for emprestimo in dados_emprestimos:
        emprestimo['_id'] = str(emprestimo['_id'])
        emprestimos_list.append(emprestimo)
    resp = {"emprestimos": emprestimos_list}
    return resp, 200

@emprestimos_bp.route('/usuarios/<id_usuario>/bikes/<id_bike>', methods=['POST'])
def post_emprestimo(id_usuario, id_bike):
    data_atual = datetime.now()

    user = mongo.db.usuarios.find_one({'_id': ObjectId(id_usuario)})
    if user is None:
        return {'erro': "Id do usuário não encontrado"}, 404

    bike = mongo.db.bikes.find_one({'_id': ObjectId(id_bike)})
    if bike is None:
        return {'erro': "Id da bike não encontrado"}, 404

    if bike['status'] != 'Disponível':
        return {'erro': 'Bike não está disponível'}, 400

    emprestimo_data = {
        'id_usuario': id_usuario,
        'id_bike': id_bike,
        'data_emprestimo': data_atual.strftime("%d/%m/%Y"),
        'data_devolucao': (data_atual + timedelta(days=1)).strftime("%d/%m/%Y")
    }

    mongo.db.bikes.update_one({'_id': ObjectId(id_bike)}, {'$set': {'status': 'Ocupado'}})

    mongo.db.emprestimos.insert_one(emprestimo_data)
    return {"mensagem": "Empréstimo registrado com sucesso"}, 201

@emprestimos_bp.route('/<id_emprestimo>', methods=['DELETE'])
def delete_emprestimo(id_emprestimo):
    result = mongo.db.emprestimos.delete_one({'_id': ObjectId(id_emprestimo)})
    if result.deleted_count == 0:
        return {'erro': "Empréstimo não encontrado"}, 404

    return {"mensagem": 'Empréstimo deletado'}, 200
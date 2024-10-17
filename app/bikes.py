from flask import Blueprint, request
from bson.objectid import ObjectId
from . import mongo

bikes_bp = Blueprint('bikes', __name__, url_prefix='/bikes')

@bikes_bp.route('/', methods=['GET'])
def get_all_bikes():
    dados_bikes = list(mongo.db.bikes.find())
    for bike in dados_bikes:
        bike['_id'] = str(bike['_id'])

    
    resp = {"bikes": list(dados_bikes)}
    return resp, 200

@bikes_bp.route('/<id_bike>', methods=['GET'])
def get_bike(id_bike):
    dados_bike = mongo.db.bikes.find_one({'_id': ObjectId(id_bike)}, {"_id": 0})
    if not dados_bike:
        return {'erro': "Bike não encontrada"}, 404

    bike_emprestimo = mongo.db.emprestimos.find_one({'id_bike': id_bike}, {'data_emprestimo': 1, '_id': 0})
    if bike_emprestimo:
        dados_bike['emprestimo'] = bike_emprestimo

    resp = {"Bike": dict(dados_bike)}
    return resp, 200

@bikes_bp.route('/', methods=['POST'])
def post_bike():
    data = request.json
    campos = ['marca', 'modelo', 'cidadeAlocada']

    for campo in campos:
        valor = data.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            return {"erro": f"O campo {campo} deve ser uma string não vazia"}, 400

    data['status'] = "Disponível"
    result = mongo.db.bikes.insert_one(data)
    return {"id": str(result.inserted_id)}, 201

@bikes_bp.route('/<id_bike>', methods=['DELETE'])
def delete_bike(id_bike):
    bike = mongo.db.bikes.find_one({'_id': ObjectId(id_bike)})
    if not bike:
        return {'erro': "Bike não encontrada"}, 404

    if bike['status'] == 'Ocupado':
        mongo.db.emprestimos.delete_many({'id_bike': id_bike})

    result = mongo.db.bikes.delete_one({'_id': ObjectId(id_bike)})
    if result.deleted_count == 0:
        return {'erro': "Bike não encontrada"}, 404

    return {"mensagem": 'Bike deletada'}, 200

@bikes_bp.route('/<id_bike>', methods=['PUT'])
def put_bike(id_bike):
    data = request.json
    dados_obrigatorios = ['marca', 'modelo', 'cidadeAlocada']

    for campo in dados_obrigatorios:
        if campo not in data:
            return {"erro": f"{campo} é obrigatório"}, 400

    new_data = {'$set': data}
    result = mongo.db.bikes.update_one({'_id': ObjectId(id_bike)}, new_data)

    if result.matched_count == 0:
        return {'erro': "Bike não encontrada"}, 404

    return {"mensagem": 'Bike atualizada'}, 200
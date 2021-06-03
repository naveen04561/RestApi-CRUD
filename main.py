from flask import Flask,jsonify,request,Response
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
import json

app = Flask(__name__)

app.config['MONGO_URI'] = "mongodb://localhost:27017/cart"

mongo = PyMongo(app)

@app.route('/')
def main():
    return "Hello"

@app.route('/add',methods=['POST'])
def add_item():
    _json = request.json
    _name = _json['name']
    _price = _json['price']
    _quantity = _json['quantity']

    if _name and _price and _quantity and request.method == 'POST':
        if not (mongo.db.items.find_one({'name': _name})):
            total_price = _price*_quantity
            id = mongo.db.items.insert_one({'name':_name, 'price':_price, 'quantity':_quantity, 'totalPrice':total_price})
            resp = jsonify("Item Added Successfully!")
            resp.status_code = 200
            return resp
        else:
            return "Item already present"
    else:
        return not_found()

@app.route('/items', methods=['GET'])
def get_items():
    items = mongo.db.items.find()
    response = json_util.dumps(items)
    return Response(response, mimetype="application/json")


@app.route('/items/<id>', methods=['GET'])
def get_item(id):
    print(id)
    item = mongo.db.items.find_one({'_id': ObjectId(id), })
    response = json_util.dumps(item)
    return Response(response, mimetype="application/json")


@app.route('/items/<id>', methods=['DELETE'])
def delete_item(id):
    mongo.db.items.delete_one({'_id': ObjectId(id)})
    response = jsonify({'message': 'Item ' + id + ' Deleted Successfully'})
    response.status_code = 200
    return response


@app.route('/items/<_id>', methods=['PUT'])
def update_item(_id):
    name = request.json['name']
    price = request.json['price']
    quantity = request.json['quantity']
    if name and price and quantity and _id:
        if (mongo.db.items.find_one({'name': name})):
            itemquantity = mongo.db.items.find_one({'name': name})['quantity']
            quantity += itemquantity
            total_price = quantity*price
            mongo.db.items.update_one(
                {'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)}, {'$set': {'name': name, 'price': price, 'quantity': quantity,'totalPrice':total_price}})
            response = jsonify({'message': 'Item ' + _id + ' Updated Successfuly'})
            response.status_code = 200
            return response
        else:
            return "Item Not Found"
    else:
      return not_found()


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'message': 'Resource Not Found ' + request.url,
        'status': 404
    }
    response = jsonify(message)
    response.status_code = 404
    return response


if __name__ == "__main__":
    app.run(debug=True)
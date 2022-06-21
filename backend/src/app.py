import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    if Drink is None:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200

@app.route('/drinks_detail')
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    try:
        drinks = Drink.query.all()

        if Drink is None:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        }), 200
    except Exception as e:
        print(e)
        abort(422)
        
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    body = request.get_json()
    try:
        drinkTitle = body['title']
        drinkRecipe = json.dumps(body['recipe'])

        newDrink = Drink(title=drinkTitle, recipe=drinkRecipe)
        newDrink.insert()

        return jsonify({
            'success': True,
            'drinks': [newDrink.long()]
        }), 200
    except Exception as e:
        print(e)
        abort(422)

    

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(id, payload):
    body = request.get_json()

    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    drink.title = body['title']
    drink.recipe = body['recipe']
    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })



@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id, payload):
    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    try:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink.id
        })

    except Exception:
        abort(422)



# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405


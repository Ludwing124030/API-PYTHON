from functools import wraps
from flask import json, request, jsonify, make_response
from jwt import decode
def auth_token_required(especialista):
    def decorator(f):
        @wraps(f)
        def wrapper_decorator(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if auth_header:
                auth_token = auth_header.split(" ")[1]
                if not auth_token: 
                    return make_response(jsonify({'message': 'a valid token is missing'}), 401)
                try: 
                    # app.config['secret']
                    data = decode(auth_token, 'secret', algorithms=["HS256"])
                    # print("especialista: ", especialista)
                    # print("usuario especialista? ", data['usuario']['especialista'])
                    if especialista and not data['usuario']['especialista']:
                        return make_response(jsonify({'message': 'esta fuera de su escala de pago'}), 403) 
                except Exception as err:
                    print(err)
                    return make_response(jsonify({'message': 'token is invalid'}), 401)
            else:
                return make_response(jsonify({"message": "request without authentication header"}), 401)    
            return f()
        return wrapper_decorator
    return decorator
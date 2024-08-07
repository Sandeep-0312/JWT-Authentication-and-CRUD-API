from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import timedelta
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Replace with your secret key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Token expiration time (adjust as needed)

jwt = JWTManager(app)

# MongoDB connection
mongo_uri = "mongodb://localhost:27017"  # Replace with your MongoDB connection string
db_name = "test"  # Database name
collection_name = "test"  # Collection name

client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]

@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    # Replace this with your authentication logic
    if username == 'your_username' and password == 'your_password':
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Authentication failed"}), 401

@app.route('/api/receive_json', methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def receive_json():
    current_user = get_jwt_identity()

    if request.method == 'GET':
        return jsonify({"message": "This is a GET request to /api/receive_json"}), 200
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if data and isinstance(data, list):
                for task in data:
                    if isinstance(task, dict):
                        collection.insert_one(task)
                    else:
                        return jsonify({"error": "Invalid JSON data format. Each task should be a dictionary."}), 400
                
                print(f"Received and inserted JSON data by {current_user}:\n{data}")
                return jsonify({"message": "JSON data received and inserted successfully"}), 201
            else:
                return jsonify({"error": "Invalid JSON data format. Expected a list of tasks."}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            if isinstance(data, dict) and 'dtId' in data:
                dtId = data['dtId']
                updated_data = collection.find_one_and_update(
                    {'dtId': dtId},
                    {'$set': data},
                    return_document=True
                )
                if updated_data:
                    print(f"Updated data for dtId {dtId} by {current_user}:\n{updated_data}")
                    return jsonify({"message": f"Document with dtId {dtId} updated successfully"}), 200
                else:
                    return jsonify({"error": f"Document with dtId {dtId} not found"}), 404
            else:
                return jsonify({"error": "Invalid JSON data format for updating. Expected a dictionary with 'dtId'."}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            if isinstance(data, dict) and 'dtId' in data:
                dtId = data['dtId']
                deleted_data = collection.find_one_and_delete({'dtId': dtId})
                if deleted_data:
                    print(f"Deleted data for dtId {dtId} by {current_user}:\n{deleted_data}")
                    return jsonify({"message": f"Document with dtId {dtId} deleted successfully"}), 200
                else:
                    return jsonify({"error": f"Document with dtId {dtId} not found"}), 404
            else:
                return jsonify({"error": "Invalid JSON data format for deleting. Expected a dictionary with 'dtId'."}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Character, Favorites  
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# User
@app.route('/user', methods=['GET'])
def get_all_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_data = {
            "email": user.email,
            "password": user.password
        }
        user_list.append(user_data)
    return jsonify(user_list), 200

@app.route ('/user/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "No user found"}), 400 
    return jsonify(user.serialize())

@app.route('/user', methods=['POST'])
def create_user():
    body = request.json
    received_data = [body.get("email"), body.get("password")]

    if None in received_data:
        return jsonify({"message": "Email and password required"}), 400

    existing_user = User.query.filter_by(email=body["email"]).first()
    if existing_user:
        return jsonify({"message": "Email already exists"}), 500

    new_user = User(email=body["email"], password=body["password"])
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as error:
        print(error)
        db.session.rollback()
        return jsonify({"message": "Failed to create user"}), 500

    return jsonify({"message": "User created successfully"}), 201

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

# PLANETS 🪐
@app.route('/planets', methods=['POST'])
def create_planet():
    if request.method == "POST":
        data = request.json
        received_data = [data.get("name"), data.get("terrain"), data.get("surface")]
        if None in received_data:
            return jsonify({"message": "There is data missing"}), 400

        #Verificamos si el planeta ya existe
        existing_planet = Planets.query.filter_by(name=data["name"]).first()
        if existing_planet:
            return jsonify({"message": "Planet already exists"})

        # Crear el planeta
        new_planet = Planets(
            name=data["name"],
            terrain=data["terrain"],
            surface=data["surface"]
        )

        # Salvar en la base de datos
        try:
            db.session.add(new_planet)
            db.session.commit()
            return jsonify({"message": "Planet created ✌️"}), 201
        except Exception as error:
            db.session.rollback()
            return jsonify({"message": "Error al crear el planeta", "error": str(error)}), 500

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    planets_list= []
    for planet in planets:
        planet_data = {
            "id": planet.id,
            "name": planet.name,
            "terrain": planet.terrain,
            "surface": planet.surface
        }
        planets_list.append(planet_data)
    return jsonify(planets_list), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({"message": "No planet found"}), 400
    return jsonify(planet.serialize()), 200

# CHARACTERS
@app.route('/characters', methods=['POST'])
def create_character():
    if request.method == "POST":
        data = request.json
        received_data = [data.get("name"), data.get("color_eyes"), data.get("height")]
        if None in received_data:
            return jsonify({"message": "Missing field"}), 400

        # Verificamos si el character existe
        existing_character = Character.query.filter_by(name=data["name"]).first()
        if existing_character:
            return jsonify({"message": "Character already exist"})

        # Crear el personaje
        new_character = Character(
            name=data["name"],
            color_eyes=data["color_eyes"],
            height=data["height"]
        )

        # Salvar en la base de datos
        try:
            db.session.add(new_character)
            db.session.commit()
            return jsonify({"message": "Character created"}), 201
        except Exception as error:
            db.session.rollback()
            return jsonify({"message": "Error al crear el personaje", "error": str(error)}), 500

@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()
    character_list = []
    for character in characters:
        character_data = {
            "id": character.id,
            "name": character.name,
            "color_eyes": character.color_eyes,
            "height": character.height
            
        }
        character_list.append(character_data)
    return jsonify(character_list), 200

@app.route('/characters/<int:characters_id>', methods=['GET'])
def get_single_character(characters_id):
    character = Character.query.get(characters_id)
    if character is None:
        return jsonify({"message": "No character found"}), 400
    return jsonify(character.serialize())

# Favorites
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    favorites = Favorites.query.filter_by(user_id=user_id).all()
    if len(favorites) < 1:
        return jsonify({"message": "Not found"}), 404
    serialized_favorites = list(map(lambda x: x.serialize(), favorites))
    """favorites_data = [favorite.serialize() for favorite in favorites]"""
    return serialized_favorites, 200

# Favorites/Planets
@app.route('/users/<int:user_id>/favorites/planets', methods=['POST'])
def add_planet_to_favorites(user_id):
    existing_user = User.query.get(user_id)
    if not existing_user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.json
    planet_id = data.get("planet_id")
    if not planet_id:
        return jsonify({"message": "Planet ID is required"}), 400
    
    existing_planet = Planets.query.get(planet_id)
    if not existing_planet:
        return jsonify({"message": "Planet not found"}), 404
    
    favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite:
        return jsonify({"message": "Planet already in favorites"}), 400
    
    new_favorite = Favorites(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify({"message": "Planet added to favorites"}), 201

@app.route('/users/<int:user_id>/favorites/planets/<int:planet_id>', methods=['DELETE'])
def remove_planet_from_favorites(user_id, planet_id):
    existing_user = User.query.get(user_id)
    if not existing_user:
        return jsonify({"message": "User not found"}), 404
    
    existing_planet = Planets.query.get(planet_id)
    if not existing_planet:
        return jsonify({"message": "Planet not found"}), 404
    
    favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"message": "Planet not found in favorites"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"message": "Planet removed from favorites"}), 200
    
# Favorites/Character
@app.route('/users/<int:user_id>/favorites/characters', methods=['POST'])
def add_character_to_favorites(user_id):
    existing_user = User.query.get(user_id)
    if not existing_user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.json
    character_id = data.get("character_id")
    if not character_id:
        return jsonify({"message": "Character ID is required"}), 400
    
    existing_character = Character.query.get(character_id)
    if not existing_character:
        return jsonify({"message": "Character not found"}), 404
    
    favorite = Favorites.query.filter_by(user_id=user_id, character_id=character_id).first()
    if favorite:
        return jsonify({"message": "Character already in favorites"}), 400
    
    new_favorite = Favorites(user_id=user_id, character_id=character_id)
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify({"message": "Character added to favorites"}), 201

@app.route('/users/<int:user_id>/favorites/characters/<int:character_id>', methods=['DELETE'])
def remove_character_from_favorites(user_id, character_id):
    existing_user = User.query.get(user_id)
    if not existing_user:
        return jsonify({"message": "User not found"}), 404
    
    existing_character = Character.query.get(character_id)
    if not existing_character:
        return jsonify({"message": "Character not found"}), 404
    
    favorite = Favorites.query.filter_by(user_id=user_id, character_id=character_id).first()
    if not favorite:
        return jsonify({"message": "Character not found in favorites"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"message": "Character removed from favorites"}), 200
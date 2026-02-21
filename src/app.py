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
from models import db, User, Person, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/people', methods=['GET'])
def get_people():
    people = Person.query.all()
    return jsonify([p.serialize_simple() for p in people]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Person.query.get_or_404(people_id)
    return jsonify(person.serialize()), 200


@app.route('/people', methods=['POST'])
def add_person():
    body = request.get_json()
    
    required_fields = ['name', 'gender', 'skin_color', 'hair_color', 'eye_color', 
                       'height', 'mass', 'birth_year', 'homeworld']
    
    for field in required_fields:
        if field not in body:
            return jsonify({"error": f"{field} is required"}), 400
    
    new_person = Person(
        name=body['name'],
        gender=body['gender'],
        skin_color=body['skin_color'],
        hair_color=body['hair_color'],
        eye_color=body['eye_color'],
        height=body['height'],
        mass=body['mass'],
        birth_year=body['birth_year'],
        homeworld=body['homeworld']
    )
    
    db.session.add(new_person)
    db.session.commit()
    
    return jsonify(new_person.serialize()), 201


@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    person = Person.query.get_or_404(people_id)
    body = request.get_json()
    
    if 'name' in body:
        person.name = body['name']
    if 'gender' in body:
        person.gender = body['gender']
    if 'skin_color' in body:
        person.skin_color = body['skin_color']
    if 'hair_color' in body:
        person.hair_color = body['hair_color']
    if 'eye_color' in body:
        person.eye_color = body['eye_color']
    if 'height' in body:
        person.height = body['height']
    if 'mass' in body:
        person.mass = body['mass']
    if 'birth_year' in body:
        person.birth_year = body['birth_year']
    if 'homeworld' in body:
        person.homeworld = body['homeworld']
    
    db.session.commit()
    
    return jsonify(person.serialize()), 200


@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    person = Person.query.get_or_404(people_id)
    
    Favorite.query.filter_by(item_type='person', item_id=people_id).delete()
    
    db.session.delete(person)
    db.session.commit()
    
    return jsonify({"message": "Person deleted successfully"}), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize_simple() for p in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    return jsonify(planet.serialize()), 200


@app.route('/planets', methods=['POST'])
def add_planet():
    body = request.get_json()
    
    required_fields = ['name', 'climate', 'diameter', 'rotation_period', 
                       'terrain', 'gravity', 'orbital_period', 'population']
    
    for field in required_fields:
        if field not in body:
            return jsonify({"error": f"{field} is required"}), 400
    
    new_planet = Planet(
        name=body['name'],
        climate=body['climate'],
        diameter=body['diameter'],
        rotation_period=body['rotation_period'],
        terrain=body['terrain'],
        gravity=body['gravity'],
        orbital_period=body['orbital_period'],
        population=body['population']
    )
    
    db.session.add(new_planet)
    db.session.commit()
    
    return jsonify(new_planet.serialize()), 201


@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    body = request.get_json()
    
    if 'name' in body:
        planet.name = body['name']
    if 'climate' in body:
        planet.climate = body['climate']
    if 'diameter' in body:
        planet.diameter = body['diameter']
    if 'rotation_period' in body:
        planet.rotation_period = body['rotation_period']
    if 'terrain' in body:
        planet.terrain = body['terrain']
    if 'gravity' in body:
        planet.gravity = body['gravity']
    if 'orbital_period' in body:
        planet.orbital_period = body['orbital_period']
    if 'population' in body:
        planet.population = body['population']
    
    db.session.commit()
    
    return jsonify(planet.serialize()), 200


@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    
    Favorite.query.filter_by(item_type='planet', item_id=planet_id).delete()
    
    db.session.delete(planet)
    db.session.commit()
    
    return jsonify({"message": "Planet deleted successfully"}), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({"error": "user_id parameter is required"}), 400
    
    user = User.query.get_or_404(user_id)
    
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([f.serialize() for f in favorites]), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    body = request.get_json()
    user_id = body.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id is required in request body"}), 400
    
    user = User.query.get_or_404(user_id)
    planet = Planet.query.get_or_404(planet_id)
    
    existing = Favorite.query.filter_by(
        user_id=user_id,
        item_type='planet',
        item_id=planet_id
    ).first()
    
    if existing:
        return jsonify({"error": "Planet already in favorites"}), 400
    
    new_favorite = Favorite(
        user_id=user_id,
        item_id=planet_id,
        item_type='planet'
    )
    
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify(new_favorite.serialize()), 201


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    body = request.get_json()
    user_id = body.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id is required in request body"}), 400
    
    user = User.query.get_or_404(user_id)
    person = Person.query.get_or_404(people_id)
    
    existing = Favorite.query.filter_by(
        user_id=user_id,
        item_type='person',
        item_id=people_id
    ).first()
    
    if existing:
        return jsonify({"error": "Person already in favorites"}), 400
    
    new_favorite = Favorite(
        user_id=user_id,
        item_id=people_id,
        item_type='person'
    )
    
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify(new_favorite.serialize()), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        body = request.get_json() or {}
        user_id = body.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    favorite = Favorite.query.filter_by(
        user_id=user_id,
        item_type='planet',
        item_id=planet_id
    ).first()
    
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"message": "Favorite planet deleted successfully"}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        body = request.get_json() or {}
        user_id = body.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    favorite = Favorite.query.filter_by(
        user_id=user_id,
        item_type='person',
        item_id=people_id
    ).first()
    
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({"message": "Favorite person deleted successfully"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)

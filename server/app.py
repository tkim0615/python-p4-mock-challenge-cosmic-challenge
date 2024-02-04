#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return 'home'

class Scientists(Resource):
    def get(self):
        scientists = [sci.to_dict(rules=('-missions',)) for sci in Scientist.query.all()]
        return make_response(scientists, 200)
    
    def post(self):
        try:
            new_sci = Scientist(
                name = request.json['name'],
                field_of_study = request.json['field_of_study']
            )
            db.session.add(new_sci)
            db.session.commit()
            return make_response(new_sci.to_dict(rules=('-missions',)), 201)
        except ValueError:
            return make_response ({
                                "errors": ["validation errors"]
                                        }, 400)

class ScientistsById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            return make_response(scientist.to_dict(), 200)
        else:
            return make_response({
                            "error": "Scientist not found"
                        }, 404)
        
    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            try:
                for attr in request.get_json():
                    setattr(scientist, attr, request.get_json()[attr])
                db.session.add(scientist)
                db.session.commit()
                return make_response(scientist.to_dict(rules=('-missions',)), 202)
            except ValueError:
                return make_response({
                                    "errors": ["validation errors"]
                                            }, 400)
        else:
            return make_response({
                                "error": "Scientist not found"
                                }, 404)
        
    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            return make_response({}, 204)
        return make_response({
                    "error": "Scientist not found"
                        }, 404)
    

class Planets(Resource):
    def get(self):
        planets = [planet.to_dict(rules=('-missions',)) for planet in Planet.query.all()]
        return make_response(planets, 200)
    
class Missions(Resource):
    def post(self):
        try:
            new_mission = Mission(
                name= request.json['name'],
                scientist_id= request.json['scientist_id'],
                planet_id= request.json['planet_id']
            )
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(), 201)
        except ValueError:
            return make_response({
                                    "errors": ["validation errors"]
                                }, 400)


api.add_resource(Scientists, '/scientists')
api.add_resource(Planets, '/planets')
api.add_resource(ScientistsById, '/scientists/<int:id>')
api.add_resource(Missions, '/missions')





if __name__ == '__main__':
    app.run(port=5555, debug=True)

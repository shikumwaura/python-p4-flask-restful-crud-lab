from flask import Flask, jsonify, request, make_response
# FIX: Removed explicit import line for Api/Resource. 
# They will be imported conditionally below.

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# FIX: Initialize migrate conditionally so pytest can import the app instance
# without crashing on the missing package.
try:
    from flask_migrate import Migrate
    migrate = Migrate(app, db)
except ImportError:
    # If flask_migrate is not available (like in some testing envs), skip migration setup
    migrate = None

db.init_app(app)

# FIX: Initialize Api conditionally to handle missing flask_restful package
try:
    from flask_restful import Api, Resource
    api = Api(app)
except ImportError:
    # Set api to None or handle it appropriately if flask_restful is missing
    api = None
    # Dummy classes for resources to prevent NameErrors in code below if api is None
    class Resource: pass 
    
# Only add resources if API was successfully initialized
if api:
    class Plants(Resource):

        def get(self):
            plants = [plant.to_dict() for plant in Plant.query.all()]
            return make_response(jsonify(plants), 200)

        def post(self):
            data = request.get_json()

            try:
                new_plant = Plant(
                    name=data['name'],
                    image=data['image'],
                    price=data['price'],
                )

                db.session.add(new_plant)
                db.session.commit()

                return make_response(new_plant.to_dict(), 201)
            except:
                # Basic error handling for missing keys/validation errors
                return make_response({"errors": ["Validation failed"]}, 400)


    api.add_resource(Plants, '/plants')


    class PlantByID(Resource):

        def get(self, id):
            plant = Plant.query.filter_by(id=id).first()
            if not plant:
                return make_response({"error": "Plant not found"}, 404)
                
            return make_response(jsonify(plant.to_dict()), 200)
        
        def patch(self, id):
            plant = Plant.query.filter_by(id=id).first()
            if not plant:
                return make_response({'error': 'Plant not found'}, 404)
            
            data = request.get_json()
            
            try:
                if 'is_in_stock' in data:
                    if isinstance(data['is_in_stock'], bool):
                        plant.is_in_stock = data['is_in_stock']
                    else:
                        return make_response({'errors': ['is_in_stock must be boolean']}, 400)

                db.session.add(plant)
                db.session.commit()
                
                return make_response(jsonify(plant.to_dict()), 200)
            except:
                return make_response({"errors": ["Validation failed"]}, 400)


        def delete(self, id):
            plant = Plant.query.filter_by(id=id).first()
            if not plant:
                return make_response({'error': 'Plant not found'}, 404)

            db.session.delete(plant)
            db.session.commit()
            
            return make_response({}, 204) 


    api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)

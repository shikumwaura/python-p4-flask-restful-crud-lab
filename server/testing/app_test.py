# File: test_app.py

import json
import pytest

from app import app, db
from models import Plant


@pytest.fixture(scope='function')
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            plant = Plant(name="Aloe", image="aloe.jpg", price=10.0, is_in_stock=True)
            db.session.add(plant)
            db.session.commit()
        yield client

        with app.app_context():
            db.drop_all()


class TestPlant:
    '''Flask application in app.py'''

    def test_plant_by_id_get_route(self, client):
        '''has a resource available at "/plants/<int:id>".'''
        response = client.get('/plants/1')
        assert response.status_code == 200

    def test_plant_by_id_get_route_returns_one_plant(self, client):
        '''returns JSON representing one Plant object at "/plants/<int:id>".'''
        response = client.get('/plants/1')
        data = json.loads(response.data.decode())

        assert isinstance(data, dict)
        assert data["id"] == 1
        assert "name" in data

    def test_plant_by_id_patch_route_updates_is_in_stock(self, client):
        '''returns JSON representing updated Plant object with "is_in_stock" = False at "/plants/<int:id>".'''
        with app.app_context():
            plant_1 = Plant.query.get(1)
            plant_1.is_in_stock = True
            db.session.commit()

        response = client.patch('/plants/1', json={"is_in_stock": False})
        data = json.loads(response.data.decode())

        assert isinstance(data, dict)
        assert data["id"] == 1
        assert data["is_in_stock"] is False

    def test_plant_by_id_delete_route_deletes_plant(self, client):
        '''returns JSON representing updated Plant object at "/plants/<int:id>".'''
        with app.app_context():
            lo = Plant(
                name="Live Oak",
                image="https://www.nwf.org/-/media/NEW-WEBSITE/Shared-Folder/Wildlife/Plants-and-Fungi/plant_southern-live-oak_600x300.ashx",
                price=250.00,
                is_in_stock=False,
            )
            db.session.add(lo)
            db.session.commit()
            plant_id = lo.id

        response = client.delete(f'/plants/{plant_id}')
        data = response.data.decode()

        assert response.status_code == 204
        assert not data
        with app.app_context():
            assert Plant.query.get(plant_id) is None

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


def executive_function():
    """
    Creating database using models,adding data to database an run the application

    """
    db.create_all()
    add_data_to_db()
    app.run(debug=True)


def add_data_to_db():
    """
    Reading json file and uoload data to database

    """
    users_list = []
    with open('users.json', 'r', encoding='utf8') as f:
        file = json.load(f)
        for user in file:
            users_list.append(User(
                id=user['id'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                age=user['age'],
                email=user['email'],
                role=user['role'],
                phone=user['phone']

            ))
        with db.session.begin():
            db.session.add_all(users_list)

        with open('orders.json', 'r', encoding='utf8') as o:
            orders_list = []

            orders_file = json.load(o)
            for order in orders_file:
                orders_list.append(Order(
                    id=order['id'],
                    name=order['name'],
                    description=order['description'],
                    start_date=datetime.strptime(order['start_date'], '%m/%d/%Y'),
                    end_date=datetime.strptime(order['end_date'], '%m/%d/%Y'),
                    price=order['price'],
                    customer_id=order['customer_id'],
                    executor_id=order['executor_id']
                ))
        with db.session.begin():
            db.session.add_all(orders_list)

    with open('offers.json', 'r', encoding='utf8') as _file:
        offer_file = json.load(_file)
        offers_list = []
        for offer in offer_file:
            offers_list.append(Offer(
                id=offer['id'],
                executor_id=offer['executor_id'],
                order_id=offer['order_id']
            ))
        with db.session.begin():
            db.session.add_all(offers_list)


@app.route('/users/', methods=['GET', 'POST'])
def get_users():
    """Get all users from database or add user to database"""
    if request.method == 'GET':
        res = []
        users = User.query.all()
        for user in users:
            res.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'age': user.age,
                'email': user.email,
                'role': user.role,
                'p:': user.phone,

            })

        return jsonify(res)

    elif request.method == 'POST':
        data = request.get_json()
        new_user = User(
            id=data['id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            email=data['email'],
            role=data['role'],
            phone=data['phone']

        )
        db.session.add(new_user)
        db.session.commit()

        return 'successfully created a new user', 200


@app.route('/users/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def get_user_by_id(uid):
    """Get user by id or update/delete user from database"""
    if request.method == 'GET':
        res = []
        user = User.query.get(uid)
        res.append({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'age': user.age,
            'email': user.email,
            'role': user.role,
            'phone:': user.phone,

        })

        return jsonify(res)

    elif request.method == 'PUT':
        data = request.get_json()
        user = User.query.get(uid)
        user.id = data['id']
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.age = data['age']
        user.email = data['email']
        user.role = data['role']
        user.phone = data['phone']

        db.session.add(user)
        db.session.commit()

        return 'successfully updated user', 201

    elif request.method == 'DELETE':
        user = User.query.get(uid)

        db.session.delete(user)
        db.session.commit

        return 'successfully deleted user', 201


@app.route('/orders/', methods=['GET', 'POST'])
def get_orders():
    """Get all orders from databae or add order to database"""
    if request.method == 'GET':
        res = []
        orders = Order.query.all()
        for order in orders:
            res.append({
                'id': order.id,
                'name': order.name,
                'description': order.description,
                'start_date': order.start_date,
                'end_date': order.end_date,
                'price': order.price,
                'customer_id': order.customer_id,
                'executor_id': order.executor_id,

            })

        return jsonify(res)

    elif request.method == 'POST':
        data = request.get_json()
        new_order = Order(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            start_date=datetime.strptime(data['start_date'], '%m/%d/%Y'),
            end_date=datetime.strptime(data['end_date'], '%m/%d/%Y'),
            price=data['price'],
            customer_id=data['customer_id'],
            executor_id=data['executor_id']
        )

        db.session.add(new_order)
        db.session.commit()

        return 'successfully added a new order', 200


@app.route('/orders/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def get_order_by_oid(oid):
    """Get order by id or update/delete order from database"""
    if request.method == 'GET':
        res = []
        order = Order.query.get(oid)
        res.append({
            'id': order.id,
            'name': order.name,
            'description': order.description,
            'start_date': order.start_date,
            'end_date': order.end_date,
            'price': order.price,
            'customer_id': order.customer_id,
            'executor_id': order.executor_id,

        })

        return jsonify(res)

    elif request.method == 'PUT':

        data = request.get_json()
        order = Order.query.get(oid)
        order.id = data['id']
        order.name = data['name']
        order.description = data['description']
        order.start_date = datetime.strptime(data['start_date'], '%m/%d/%Y')
        order.end_date = datetime.strptime(data['end_date'], '%m/%d/%Y')
        order.price = data['price']
        order.customer_id = data['customer_id']
        order.executor_id = data['executor_id']

        db.session.add(order)
        db.session.commit()

        return 'successfully updated order', 201

    elif request.method == 'DELETE':
        order = Order.query.get(oid)

        db.session.delete(order)
        db.session.commit

        return 'successfully deleted order', 201


@app.route('/offers/', methods=['GET', 'POST'])
def get_offers():
    """Get all offers or add offer from/to database"""
    if request.method == 'GET':
        res = []
        offers = Offer.query.all()
        for offer in offers:
            res.append({
                'id': offer.id,
                'executor_id': offer.executor_id,
                'order_id': offer.order_id

            })

        return jsonify(res)

    elif request.method == 'POST':
        data = request.get_json()
        new_offer = Offer(
            id=data['id'],
            executor_id=data['executor_id'],
            order_id=data['order_id']
        )

        db.session.add(new_offer)
        db.session.commit()

        return 'successfully added a new offer', 200


@app.route('/offers/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def get_offer_by_oid(oid):
    """Get offer by id or update/delete offer from database"""
    if request.method == 'GET':
        res = []
        offer = Offer.query.get(oid)
        res.append({
            'id': offer.id,
            'executor_id': offer.executor_id,
            'order_id': offer.order_id

        })
        return jsonify(res)

    elif request.method == 'PUT':
        data = request.get_json()
        offer = Offer.query.get(oid)
        offer.id = data['id']
        offer.executor_id = data['executor_id']
        offer.order_id = data['order_id']

        db.session.add(offer)
        db.session.commit()

        return 'successfully updated offer', 201

    elif request.method == 'DELETE':
        offer = Offer.query.get(oid)

        db.session.delete(offer)
        db.session.commit()

        return 'successfully deleted offer', 201


if __name__ == '__main__':
    executive_function()


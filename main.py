from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
import re

app = Flask(__name__)
app.json.sort_keys = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    owes_to = db.relationship('Transaction', backref='debtor_user', lazy=True, foreign_keys='[Transaction.debtor_id]')
    owed_by = db.relationship('Transaction', backref='creditor_user', lazy=True, foreign_keys='[Transaction.creditor_id]')

    @property
    def sum(self):
        owed = db.session.query(func.sum(Transaction.amount)).filter_by(creditor_id=self.id).scalar() or 0
        owes = db.session.query(func.sum(Transaction.amount)).filter_by(debtor_id=self.id).scalar() or 0
        return owed - owes

    def __repr__(self):
        return f"User(name='{self.name}')"

    def to_dict(self):
        return {
            'name': self.name,
            'owes_to': {t.creditor_user.name: t.creditor_user.total_owed_to(self) for t in self.owes_to},
            'owed_by': {t.debtor_user.name: t.debtor_user.total_owed_by(self) for t in self.owed_by},
            'sum': self.sum
        }

    def total_owed_to(self, other_user):
        total = db.session.query(func.sum(Transaction.amount)).filter_by(
            creditor_id=self.id, debtor_id=other_user.id
        ).scalar()
        return total or 0

    def total_owed_by(self, other_user):
        total = db.session.query(func.sum(Transaction.amount)).filter_by(
            creditor_id=other_user.id, debtor_id=self.id
        ).scalar()
        return total or 0


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    creditor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    debtor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creditor = db.relationship('User', foreign_keys=[creditor_id], overlaps='creditor_user, owed_by')
    debtor = db.relationship('User', foreign_keys=[debtor_id], overlaps='debtor_user,owes_to')

    def __repr__(self):
        return f"Transaction(creditor='{self.creditor.name}', debtor='{self.debtor.name}', amount={self.amount})"


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        '/all_users/': 'Show all users',
        '/user/<name>': 'Show a single user',
        '/add/': 'Add a new user (expects payload)',
        '/transaction': 'Add a new transaction (expects payload)'
    }), 200


@app.route('/all_users/', methods=['GET'])
def all_users():
    users = User.query.all()
    return jsonify({'all_users': [user.to_dict() for user in users]}), 200


@app.route('/user/<string:username>/', methods=['GET'])
def show_user(username):
    user = User.query.filter_by(name=username).first()
    if not user:
        return jsonify({'message': 'User not found.'}), 404
    return jsonify({'user': user.to_dict()}), 200


@app.route('/add/', methods=['POST'])
def add_user():
    if not request.is_json:
        return jsonify({'message': 'Request must be in JSON format.'}), 400
    try:
        name = request.json.get('name')
    except AttributeError:
        return jsonify({'message': 'Request is incorrectly formatted.'}), 400
    if not name:
        return jsonify({'message': 'Name is required.'}), 400
    pattern = re.compile(r'^[a-zA-Z]+[a-zA-Z0-9]*$')
    if not pattern.match(str(name)):
        return jsonify({'message': 'Username cannot start with a number (but can contain them).'}), 400
    user = User(name=name)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': f'User {name} already exists.'}), 409
    return jsonify(user.to_dict()), 201


@app.route('/transaction/', methods=['POST'])
def add_transaction():
    if not request.is_json:
        return jsonify({'message': 'Request must be in JSON format.'}), 400
    data = request.get_json()
    if not type(data) == dict:
        return jsonify({'message': 'Request is incorrectly formatted.'}), 400
    try:
        creditor = User.query.filter_by(name=data['creditor']).first()
        debtor = User.query.filter_by(name=data['debtor']).first()
        amount = data['amount']
    except KeyError:
        return jsonify({'message': 'Some of the required fields are missing.'}), 400
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({'message': 'Amount must be a positive number.'}), 400
    if creditor == debtor:
        return jsonify({'message': 'A user cannot owe money to themselves.'}), 400
    transaction = Transaction(creditor=creditor, debtor=debtor, amount=amount)
    db.session.add(transaction)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'One of the users does not exist.'}), 400
    both = [creditor, debtor]
    sort = sorted(both, key=lambda k: k.to_dict()['name'])
    return jsonify({'users': [user.to_dict() for user in sort]}), 201

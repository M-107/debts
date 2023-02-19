from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    owes_to = db.relationship('Transaction', backref='creditor_user', lazy=True, foreign_keys="[Transaction.creditor_id]")
    owed_by = db.relationship('Transaction', backref='debtor_user', lazy=True, foreign_keys="[Transaction.debtor_id]")

    @property
    def sum(self):
        return sum(t.amount for t in self.owed_by) - sum(t.amount for t in self.owes_to)

    def __repr__(self):
        return f"User(name='{self.name}')"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'owes_to': {t.creditor_user.name: t.amount for t in self.owes_to},
            'owed_by': {t.debtor_user.name: t.amount for t in self.owed_by},
            'sum': self.sum
        }


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    creditor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    debtor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    creditor = db.relationship('User', foreign_keys=[creditor_id])
    debtor = db.relationship('User', foreign_keys=[debtor_id])

    def __repr__(self):
        return f"Transaction(creditor='{self.creditor.name}', debtor='{self.debtor.name}', amount={self.amount})"


@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return jsonify([{
        "name": user.name,
        "sum": user.sum
    } for user in users])


@app.route('/user/<string:username>/', methods=['GET'])
def show_user(username):
    user = User.query.filter_by(name=username).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(user.to_dict()), 201


@app.route('/add/', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'message': 'Name is required'}), 400

    user = User(name=name)
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': f'User {name} already exists'}), 409

    return jsonify(user.to_dict()), 201


@app.route('/transaction/', methods=['POST'])
def add_transaction():
    data = request.get_json()
    creditor = User.query.filter_by(name=data['creditor']).first()
    debtor = User.query.filter_by(name=data['debtor']).first()
    amount = data['amount']
    transaction = Transaction(creditor=creditor, debtor=debtor, amount=amount)
    db.session.add(transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction added successfully!'})

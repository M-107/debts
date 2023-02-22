import unittest
from main import app, db, User


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        with app.app_context():
            db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()


class IndexTest(TestCase):
    def test_index(self):
        response = self.client.get('/')
        expected_response = {
            '/all_users/': 'Show all users',
            '/user/<name>': 'Show a single user',
            '/add/': 'Add a new user (expects payload)',
            '/transaction': 'Add a new transaction (expects payload)'
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_response)


class UserTests(TestCase):
    def test_add_user(self):
        data = {'name': 'Adam'}
        response = self.client.post('/add/', json=data)
        expected_response = {
            'name': 'Adam',
            'owes_to': {},
            'owed_by': {},
            'sum': 0
        }
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, expected_response)

    def test_all_users(self):
        response = self.client.get('/all_users/')
        expected_response = {'all_users': []}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_response)

    def test_show_user(self):
        with app.app_context():
            db.session.add(User(name='Adam'))
            db.session.commit()
        response = self.client.get('/user/Adam/')
        expected_response = {
            'user': {
                'name': 'Adam',
                'owes_to': {},
                'owed_by': {},
                'sum': 0
            }
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, expected_response)

    def test_show_wrong_user(self):
        response = self.client.get('/user/Karel/')
        expected_response = {'message': 'User not found.'}
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, expected_response)

    def test_add_not_json(self):
        data = "Marek"
        response = self.client.post('/add/', json=data)
        expected_response = {'message': 'Request is incorrectly formatted.'}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_response)

    def test_add_empty_name(self):
        response = self.client.post('/add/', json={})
        expected_response = {'message': 'Name is required.'}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_response)

    def test_add_name_starting_number(self):
        data = {'name': '5Marek'}
        response = self.client.post('/add/', json=data)
        self.assertEqual(response.status_code, 400)
        expected_response = {'message': 'Username cannot start with a number (but can contain them).'}
        self.assertEqual(response.json, expected_response)

    def test_add_user_twice(self):
        with app.app_context():
            db.session.add(User(name='Adam'))
            db.session.commit()
            data = {'name': 'Adam'}
            response = self.client.post('/add/', json=data)
        expected_response = {'message': 'User Adam already exists.'}
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json, expected_response)


class TransactionTests(TestCase):
    def test_add_transaction(self):
        with app.app_context():
            db.session.add(User(name='Petr'))
            db.session.add(User(name='Martin'))
            db.session.commit()
            data = {'creditor': 'Petr', 'debtor': 'Martin', 'amount': 100.0}
            response = self.client.post('/transaction/', json=data)
        expected_response = {
            'users': [
                {
                    'name': 'Martin',
                    'owes_to': {'Petr': 100.0},
                    'owed_by': {},
                    'sum': -100.0
                },
                {
                    'name': 'Petr',
                    'owes_to': {},
                    'owed_by': {'Martin': 100.0},
                    'sum': 100.0
                }
            ]
        }
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, expected_response)

    def test_transaction_not_json(self):
        data = "Petr, Karel, 100"
        response = self.client.post('/transaction/', json=data)
        expected_response = {'message': 'Request is incorrectly formatted.'}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_response)

    def test_incomplete_json(self):
        data = {'creditor': 'Petr', 'amount': 100.0}
        response = self.client.post('/transaction/', json=data)
        expected_response = {'message': 'Some of the required fields are missing.'}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_response)

    def test_worng_amount_format(self):
        data = {'creditor': 'Petr', 'debtor': 'Martin', 'amount': -100.0}
        response = self.client.post('/transaction/', json=data)
        expected_response = {'message': 'Amount must be a positive number.'}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_response)

    def test_same_creditor_debtor(self):
        data = {'creditor': 'Petr', 'debtor': 'Petr', 'amount': 100.0}
        response = self.client.post('/transaction/', json=data)
        expected_response = {'message': 'A user cannot owe money to themselves.'}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_response)

    def test_nonexistend_user(self):
        with app.app_context():
            db.session.add(User(name='Petr'))
            db.session.commit()
        data = {'creditor': 'Petr', 'debtor': 'Karel', 'amount': 100.0}
        response = self.client.post('/transaction/', json=data)
        expected_response = {'message': 'One of the users does not exist.'}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, expected_response)


if __name__ == '__main__':
    unittest.main()

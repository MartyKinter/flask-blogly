from unittest import TestCase
from app import app, db
from models import User


class FlaskTests(TestCase):

    def setUp(self):
        """Set up database for testing"""
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly_test"
        app.config['TESTING'] = True

        with app.app_context():
            self.client = app.test_client()
            db.drop_all()
            db.create_all()

            user = User(first_name="Test", last_name="User")
            db.session.add(user)
            db.session.commit()

            self.user_id = user.id


    def tearDown(self):
        """Clean up database after testing"""
        with app.app_context():
            db.session.rollback()


    def test_homepage_redirect(self):
        """Test if homepage redirects to users page"""

        with self.client as client:
            response = client.get("/")
            self.assertEqual(response.status_code, 302)


    def test_user_list(self):
        """Test if user list page displays all users"""

        with self.client as client:
            response = client.get("/users")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Test User", response.data)


    def test_new_user_page(self):
        """Test if new user page is displayed"""

        with self.client as client:
            response = client.get("/users/new")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Create a user", response.data)


    def test_create_new_user(self):
        """Test if new user is created"""

        with self.client as client:
            response = client.post("/users/new", data={"first_name": "John", "last_name": "Doe"})

            user = User.query.filter_by(first_name="John", last_name="Doe").all()
            self.assertIsNotNone(user)


from unittest import TestCase
from app import app, db
from models import User, Post, Tag


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

            post1 = Post(title='test_title', content='test_content', user_id=user.id)
            post2 = Post(title="test_title_2", content="Test Content 2", user_id=user.id)
            db.session.add_all([post1, post2])            
            db.session.commit()

            tag1 = Tag(name="Test Tag 1", posts=[post1])
            tag2 = Tag(name="Test Tag 2", posts=[post2])
            db.session.add_all([tag1, tag2])
            db.session.commit()

            self.user_id = user.id
            self.tag1_id = tag1.id
            self.tag2_id = tag2.id
            self.post1_id = post1.id
            self.post2_id = post2.id


    def tearDown(self):
        """Clean up database after testing"""
        with app.app_context():
            db.session.rollback()


    def test_homepage_redirect(self):
        """Test if homepage redirects to users page"""

        with self.client as client:
            response = client.get("/")
            self.assertEqual(response.status_code, 200)


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

    def test_create_post(self):
        """Test if new post is created for a specific user"""

        with self.client as client:
            response = client.post(f"/users/{self.user_id}/posts/new", data={"title": "Test Post", "content": "Test Content"})

            post = Post.query.filter_by(title="Test Post", content="Test Content", user_id=self.user_id).first()
            self.assertEqual(post.title, 'Test Post')
            self.assertEqual(post.content, 'Test Content')

    def test_post_details(self):
        response = self.app.get(f'/posts/{self.post.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('test_title', str(response.data))

    def test_post_details(self):
        """Test if post details page is displayed"""

        with self.client as client:
            with app.app_context():
                post = Post.query.first()
                response = client.get(f"/posts/{post.id}")
                self.assertIn(b"test_title", response.data)

    def test_edit_post_page(self):
        """Test if edit post page is displayed"""

        with self.client as client:
            with app.app_context():
                post = Post.query.first()
                response = client.get(f"/posts/{post.id}/edit")
                self.assertIn(b"test_title", response.data)

    def test_update_post(self):
        """Test if existing post is updated"""

        with self.client as client:
            with app.app_context():
                post = Post.query.first()
                response = client.post(f"/posts/{post.id}/edit", data={"title": "Updated Post Title", "content": "Updated Post Content"})

                updated_post = Post.query.filter_by(id=post.id).first()
                self.assertEqual(updated_post.title, "Updated Post Title")
                self.assertEqual(updated_post.content, "Updated Post Content")


    def test_all_tags(self):
        """Test if all tags are displayed on the tags index page"""

        with self.client as client:
            response = client.get("/tags")
            self.assertIn(b"Test Tag 1", response.data)
            self.assertIn(b"Test Tag 2", response.data)


    def test_new_tag_form(self):
        """Test if new tag form is displayed"""

        with self.client as client:
            response = client.get("/tags/new")
            self.assertIn(b"Create a tag", response.data)


    def test_new_tag(self):
        """Test if a new tag is created"""

        with self.client as client:
            with app.app_context():
                response = client.post("/tags/new", data={"name": "New Tag", "posts": [str(self.post2_id)]})

                tag = Tag.query.filter_by(name="New Tag").first()
                self.assertEqual(tag.name, "New Tag")


    def test_tag_details(self):
        """Test if tag details are displayed on the tag details page"""

        with self.client as client:
            response = client.get(f"/tags/{self.tag1_id}")
            self.assertIn(b"Test Tag 1", response.data)
            self.assertIn(b"test_title", response.data)

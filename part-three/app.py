from flask import Flask, request, redirect, render_template, flash
from models import db, connect_db, User, Post, Tag


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secret'

connect_db(app)
with app.app_context():
    db.create_all()


@app.errorhandler(404)
def page_not_found(e):
    """page not found"""
    return render_template('404.html'), 404

@app.route('/')
def homepage():
    """Display posts, most-recent first"""
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()

    return render_template("/posts/homepage.html", posts=posts)


@app.route('/users')
def user_list():
    """Displays lists of all users"""

    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('users/index.html', users=users)


@app.route('/users/new', methods=["GET"])
def new_user():
    """Display page to create new user"""

    return render_template('users/new.html')


@app.route("/users/new", methods=["POST"])
def create_new():
    """Handle form submission for creating a new user and go to homepage"""

    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None)

    db.session.add(new_user)
    db.session.commit()
    flash(f"User {new_user.first_name} added.")

    return redirect("/users")


@app.route('/users/<int:user_id>')
def user_details(user_id):
    """Display info for specific user or 404 if no user for that id"""

    user = User.query.get_or_404(user_id)
    return render_template('users/details.html', user=user)


@app.route('/users/<int:user_id>/edit')
def edit_page(user_id):
    """Display page for editing a users info, 404 if no user for id"""

    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def edit_user(user_id):
    """Handle form submission for updating an existing user"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()
    flash(f"User {user.full_name} edited.")

    return redirect("/users")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """Handle form submission for deleting an existing user"""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.full_name} deleted.")

    return redirect("/users")


@app.route('/users/<int:user_id>/posts/new')
def new_post_form(user_id):
    """Display new post form"""

    user = User.query.get_or_404(user_id)
    return render_template('posts/new.html', user=user)


@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def create_post(user_id):
    """Handle form submission for creating a new post for a specific user"""

    user = User.query.get_or_404(user_id)
    new_post = Post(title=request.form['title'],
                    content=request.form['content'],
                    user=user)

    db.session.add(new_post)
    db.session.commit()
    flash(f"Post '{new_post.title}' added.")

    return redirect(f"/users/{user_id}")


@app.route('/posts/<int:post_id>')
def post_details(post_id):
    """Display page with details about specific post"""
    post = Post.query.get_or_404(post_id)

    return render_template('posts/details.html', post=post)


@app.route('/posts/<int:post_id>/edit')
def edit_post(post_id):
    """Display form to exit a post"""

    post = Post.query.get_or_404(post_id)
    return render_template('posts/edit.html', post=post)


@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def update_post(post_id):
    """Handle submission to update post"""

    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    db.session.add(post)
    db.session.commit()
    flash(f"Post '{post.title} edited.")

    return redirect(f"/users/{post.user_id}")


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def posts_delete(post_id):
    """Handle deleting an existing post"""

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()
    flash(f"Post '{post.title}' deleted.")

    return redirect(f"/users/{post.user_id}")


@app.route("/tags")
def all_tags():
    """Display page with info of all tags"""

    tags = Tag.query.all()
    return render_template('tags/index.html', tags=tags)


@app.route('/tags/new')
def new_tag_form():
    """Form to create a new tag"""

    posts = Post.query.all()
    return render_template('tags/new.html', posts=posts)


@app.route("/tags/new", methods=["POST"])
def new_tag():
    """Handle submission of new tag form"""

    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    new_tag = Tag(name=request.form['name'], posts=posts)

    db.session.add(new_tag)
    db.session.commit()
    flash(f"Tag '{new_tag.name}' added.")

    return redirect("/tags")


@app.route('/tags/<int:tag_id>')
def tag_details(tag_id):
    """Display page with details about specific tag"""

    tag = Tag.query.get_or_404(tag_id)
    return render_template("tags/details.html", tag=tag)


@app.route('/tags/<int:tag_id>/edit')
def edit_tag_form(tag_id):
    """Display form for editing a tag"""

    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('tags/edit.html', tag=tag, posts=posts)


@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def edit_tag(tag_id):
    """Handle form submission for editing a tag"""

    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' edited.")

    return redirect("/tags")


@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def delete_tag(tag_id):
    """Handle deleting a tag"""

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash(f"Tag '{tag.name}' deleted.")

    return redirect("/tags")
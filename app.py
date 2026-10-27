import os
import secrets

from flask import Flask, session, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)

# ==================== CONFIGURATION ====================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = "your-secret-key-change-this"

# New session version every time the application restarts
app.config["SESSION_VERSION"] = secrets.token_hex(16)

app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path,
    "static",
    "uploads",
    "books"
)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)


# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def is_logged_in():
    return (
        "user_id" in session
        and session.get("session_version") == app.config["SESSION_VERSION"]
    )


# ==================== SESSION VALIDATION ====================

@app.before_request
def validate_session():
    if "user_id" in session:
        if session.get("session_version") != app.config["SESSION_VERSION"]:
            session.clear()


# ==================== MODELS ====================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    # Owner of the book
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    image = db.Column(db.String(255))


# ==================== HOME ====================

@app.route("/")
def home():

    if not is_logged_in():
        session.clear()
        flash("Please login to view the books.", "warning")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if not user:
        session.clear()
        flash("User account not found. Please login again.", "danger")
        return redirect(url_for("login"))

    # ONLY books belonging to the logged-in user
    books = Book.query.filter_by(
        user_id=user.id
    ).order_by(Book.id.desc()).all()

    return render_template("home.html", books=books)


# ==================== REGISTER ====================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not all([name, email, phone, password]):
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "warning")
            return redirect(url_for("register"))

        user = User(
            name=name,
            email=email,
            phone=phone,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


# ==================== LOGIN ====================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            # Store current logged-in user
            session["user_id"] = user.id

            # Store current application session version
            session["session_version"] = app.config["SESSION_VERSION"]

#            flash("Login successful!", "success")
            return redirect(url_for("home"))

        flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")



# ==================== LOGOUT ====================

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("session_version", None)
#    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# ==================== PROFILE ====================

@app.route("/profile")
def profile():
    if not is_logged_in():
        session.clear()
        flash("Please login again.", "warning")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user:
        session.clear()
        flash("User account not found.", "danger")
        return redirect(url_for("login"))

    # ONLY show books uploaded by the current logged-in user
    books = Book.query.filter_by(
        user_id=user.id).order_by(Book.id.desc()).all()

    return render_template("profile.html", user=user, books=books)


# ==================== ADD BOOK ====================

@app.route("/books/add", methods=["GET", "POST"])
def add_book():

    if not is_logged_in():
        session.clear()
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        price = request.form.get("price", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        image = request.files.get("image")
        image_name = None

        if not title or not author or not price:

            flash(
                "Title, author and price are required.",
                "danger"
            )

            return render_template("add_book.html")

        try:

            price = float(price)

            if image and image.filename:
                if not allowed_file(image.filename):
                    flash(
                        "Only PNG, JPG, JPEG and WEBP images are allowed.",
                        "danger"
                    )
                    return render_template("add_book.html")
                image_name = secure_filename(image.filename)

                image.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        image_name
                    )
                )

            # Associate this book with the current logged-in user
            book = Book(
                user_id=session["user_id"],
                title=title,
                author=author,
                price=price,
                category=category,
                description=description,
                image=image_name
            )

            db.session.add(book)
            db.session.commit()

#            flash("Book added successfully.", "success")

            return redirect(url_for("profile"))

        except ValueError:

            flash(
                "Please enter a valid price.",
                "danger"
            )

    return render_template("add_book.html")


# ==================== EDIT BOOK ====================

@app.route("/books/edit/<int:id>", methods=["GET", "POST"])
def edit_book(id):

    if not is_logged_in():
        session.clear()
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    # Only find a book that belongs to the current user
    book = Book.query.filter_by(id=id, user_id=session["user_id"]).first()

    if not book:

        flash(
            "Book not found or you do not have permission to edit it.",
            "danger"
        )

        return redirect(url_for("profile"))

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        price = request.form.get("price", "").strip()

        if not title or not author or not price:

            flash(
                "Title, author and price are required.",
                "danger"
            )

            return render_template("edit_book.html", book=book)

        try:

            book.title = title
            book.author = author
            book.price = float(price)
            book.category = request.form.get("category", "").strip()
            book.description = request.form.get("description", "").strip()
            image = request.files.get("image")

            if image and image.filename:

                if not allowed_file(image.filename):

                    flash(
                        "Only PNG, JPG, JPEG and WEBP images are allowed.",
                        "danger"
                    )

                    return render_template(
                        "edit_book.html",
                        book=book
                    )

                image_name = secure_filename(
                    image.filename
                )

                image.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        image_name
                    )
                )

                book.image = image_name

            db.session.commit()

#            flash("Book updated successfully.", "success")

            return redirect(url_for("profile"))

        except ValueError:

            flash("Please enter a valid price.", "danger")

    return render_template("edit_book.html", book=book)


# ==================== DELETE BOOK ====================

@app.route("/books/delete/<int:id>", methods=["POST"])
def delete_book(id):

    if not is_logged_in():

        session.clear()

        flash(
            "Please login to delete a book.",
            "warning"
        )

        return redirect(url_for("login"))

    # Only allow the current user to delete THEIR OWN book
    book = Book.query.filter_by(id=id, user_id=session["user_id"]).first()

    if not book:

        flash("Book not found or you do not have permission to delete it.", "danger")

        return redirect(url_for("profile"))

    # Delete image from uploads folder
    if book.image:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], book.image)

        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(book)
    db.session.commit()

    return redirect(url_for("profile"))


# ==================== RUN ====================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)


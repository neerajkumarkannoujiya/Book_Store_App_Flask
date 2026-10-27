# 📚 BookNest — Flask Book Store

BookNest is a modern and responsive **bookstore web application built with Flask and SQLite**.  
It allows users to create an account, log in securely, browse books, and manage book listings through a simple and clean interface.

The application demonstrates core concepts of **Flask web development, MVC-style application structure, SQLAlchemy ORM, authentication, CRUD operations, file uploads, Jinja templating, and Bootstrap-based responsive UI**.

---

## ✨ Features

### 👤 User Authentication

- User registration
- User login and logout
- Password hashing using Werkzeug
- Session-based authentication
- Email uniqueness validation
- Password confirmation during registration
- Protected profile and book-management routes

### 📖 Book Management

Authenticated users can:

- Add new books
- Edit existing books
- Delete books
- View all available books
- Add book title, author, price, category, and description
- Upload book cover images
- Replace existing book cover images

### 🖼️ Image Upload

BookNest supports actual image uploads instead of storing image URLs.

Supported formats:

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`

Uploaded images are stored in:

```text
static/uploads/books/

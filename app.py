from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os


# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma =Marshmallow(app)

# User Class/Model
class User(db.Model):
    user_id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(100), unique=True)

    def __init__(self, username):
        self.username = username

# Book Class/Model
class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key = True)
    book_name = db.Column(db.String(100))
    genre = db.Column(db.String(100))
    author = db.Column(db.String(100))

    def __init__(self, book_name, genre, author):
        self.book_name = book_name
        self.genre = genre
        self.author = author

# Seles Class/Model
class Sales(db.Model):
    sales_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.String(100))
    book_id = db.Column(db.String(100))

    def __init__(self, user_id, book_id):
        self.user_id = user_id
        self.book_id = book_id

# User Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('user_id', 'username')

# Book Schema
class BookSchema(ma.Schema):
    class Meta:
        fields = ('book_id', 'book_name', 'genre' , 'author')

# Sales Schema
class SalesSchema(ma.Schema):
    class Meta:
        fields = ('sales_id', 'user_id', 'book_id')


# Init Schema
user_schema = UserSchema()
book_schema = BookSchema()
books_schema = BookSchema(many=True)
sales_schema = SalesSchema()

# Routing for user creation
@app.route('/user', methods=['POST'])
def add_user():
    username = request.json['username']

    new_user = User(username)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)

# getting user data
@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    return user_schema.jsonify(user)

# updating user data
@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    user.username = request.json['username']
    db.session.commit()
    return user_schema.jsonify(user)


# deleting user data
@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    sales = Sales.query.all()
    for sale in sales:
        if sale.user_id == user_id:
            db.session.delete(sale)
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)

# creation of book data
@app.route('/book', methods=['POST'])
def add_book():
    book_name = request.json['book_name']
    genre = request.json['genre']
    author = request.json['author']

    new_book = Book(book_name, genre, author)
    db.session.add(new_book)
    db.session.commit()
    return book_schema.jsonify(new_book)

# getting single book details
@app.route('/book/<book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get(book_id)
    return book_schema.jsonify(book)

# getting books details
@app.route('/book', methods=['GET'])
def get_books():
    books = Book.query.all()
    result = books_schema.dump(books)
    return books_schema.jsonify(result)

# updating single book details
@app.route('/book/<book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get(book_id)
    book.book_name = request.json['book_name']
    book.genre = request.json['genre']
    book.author = request.json['author']
    db.session.commit()
    return book_schema.jsonify(book)
  
# deleting single book details
@app.route('/book/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    sales = Sales.query.all()
    for sale in sales:
        if sale.book_id == book_id:
            db.session.delete(sale)
    book = Book.query.get(book_id)
    db.session.delete(book)
    db.session.commit()
    return book_schema.jsonify(book)
  
# creating a sales record
@app.route('/sale', methods=['POST'])
def create_sale():
    user_id = request.json['user_id']
    book_id = request.json['book_id']
    new_sale = Sales(user_id, book_id)
    db.session.add(new_sale)
    db.session.commit()
    return sales_schema.jsonify(new_sale)

# getting a sales record
@app.route('/sale/<sales_id>', methods=['GET'])
def get_sale(sales_id):
    sale  = Sales.query.get(sales_id)
    return sales_schema.jsonify(sale)

# deleting a sales record
@app.route('/sale/<sales_id>', methods=['DELETE'])
def update_sale(sales_id):
    sale = Sales.query.get(sales_id)
    db.session.delete(sale)
    db.session.commit()
    return sales_schema.jsonify(sale)

# query
@app.route('/query', methods=['GET'])
def query():
    all_sales = Sales.query.all()

    d = {}
    for sale in all_sales:
        book = Book.query.get(sale.book_id)
        if book.genre == 'software architecture':
            if book.book_id in d:
                val = d[book.book_id]
                val = val + 1
                d[book.book_id] = val

            else:
                val = 1
                d[book.book_id] = val
    
    max_val = 0
    book_id = 0

    for book in d:
        if d[book] > max_val:
            max_val = d[book]
            book_id = book
        
    book_to_return = Book.query.get(book_id)
    return book_schema.jsonify(book_to_return)

# Run server
if __name__ == '__main__':
    app.run(debug=True)
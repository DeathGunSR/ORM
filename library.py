from peewee import SqliteDatabase, Model, IntegerField, CharField, ForeignKeyField
from peewee import OperationalError, IntegrityError
import sqlite3


db = SqliteDatabase('library.db')

class BaseModel(Model):
    class Meta:
        database = db

class Book(BaseModel):
    table_name = 'books'
    id = IntegerField(primary_key=True)
    title = CharField(max_length=127, null=True)
    author = CharField(max_length=255)
    year = IntegerField(null=True)
    total_copies = IntegerField(default=1)
    lent_copies = IntegerField(default=0)

    @staticmethod
    def create_table():
        """Create the books table"""
        try:
            with db.connection_context():
                db.execute_sql("""
                    CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        author TEXT NOT NULL,
                        year INTEGER,
                        total_copies INTEGER NOT NULL DEFAULT 1,
                        lent_copies INTEGER NOT NULL DEFAULT 0
                    )
                """)
            print("Books table created successfully.")
        except OperationalError as e:
            print(f"Error creating books table: {e}")

    def save(self):
        """Save or update a book"""
        try:
            with db.connection_context():
                if self.id is None:
                    cursor = db.execute_sql(
                        "INSERT INTO books (title, author, year, total_copies, lent_copies) VALUES (?, ?, ?, ?, ?)",
                        (self.title, self.author, self.year, self.total_copies, self.lent_copies)
                    )
                    self.id = cursor.lastrowid
                    print(f"Book '{self.title}' added successfully.")
                else:
                    result = db.execute_sql(
                        "UPDATE books SET title = ?, author = ?, year = ?, total_copies = ?, lent_copies = ? WHERE id = ?",
                        (self.title, self.author, self.year, self.total_copies, self.lent_copies, self.id)
                    )
                    if result.rowcount > 0:
                        print(f"Book with ID {self.id} updated successfully.")
                    else:
                        print(f"Book with ID {self.id} not found.")
        except IntegrityError as e:
            print(f"Error saving book: {e}")

    @staticmethod
    def get(title=None, author=None):
        """Retrieve a book by title or author"""
        try:
            with db.connection_context():
                query = "SELECT id, title, author, year, total_copies, lent_copies FROM books WHERE "
                params = []
                conditions = []
                if title:
                    conditions.append("title LIKE ?")
                    params.append(f"%{title}%")
                if author:
                    conditions.append("author LIKE ?")
                    params.append(f"%{author}%")
                if not conditions:
                    raise ValueError("At least one of title or author must be provided.")
                query += " OR ".join(conditions)
                cursor = db.execute_sql(query, params)
                row = cursor.fetchone()
                if row:
                    return Book(id=row[0], title=row[1], author=row[2], year=row[3], total_copies=row[4], lent_copies=row[5])
                else:
                    raise ValueError(f"Book with title '{title}' or author '{author}' not found.")
        except Exception as e:
            print(f"Error retrieving book: {e}")
            raise

    def delete(self):
        """Delete a book"""
        try:
            with db.connection_context():
                result = db.execute_sql(
                    "DELETE FROM books WHERE id = ?",
                    (self.id,)
                )
                if result.rowcount > 0:
                    print(f"Book with ID {self.id} deleted successfully.")
                    self.id = None
                else:
                    print(f"Book with ID {self.id} not found.")
        except Exception as e:
            print(f"Error deleting book: {e}")

class User(BaseModel):
    table_name = 'users'
    id = IntegerField(primary_key=True)
    first_name = CharField(max_length=127, null=True)
    last_name = CharField(max_length=127, null=True)
    age = IntegerField()
    gender = CharField(max_length=10)
    email = CharField(max_length=255, unique=True)

    @staticmethod
    def create_table():
        """Create the users table"""
        try:
            with db.connection_context():
                db.execute_sql("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT,
                        last_name TEXT,
                        age INTEGER NOT NULL,
                        gender TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE
                    )
                """)
            print("Users table created successfully.")
        except OperationalError as e:
            print(f"Error creating users table: {e}")

    def save(self):
        """Save or update a user"""
        try:
            if self.age < 15:
                raise ValueError("User must be at least 15 years old.")
            with db.connection_context():
                if self.id is None:
                    cursor = db.execute_sql(
                        "INSERT INTO users (first_name, last_name, age, gender, email) VALUES (?, ?, ?, ?, ?)",
                        (self.first_name, self.last_name, self.age, self.gender, self.email)
                    )
                    self.id = cursor.lastrowid
                    print(f"User with email {self.email} added successfully.")
                else:
                    result = db.execute_sql(
                        "UPDATE users SET first_name = ?, last_name = ?, age = ?, gender = ?, email = ? WHERE id = ?",
                        (self.first_name, self.last_name, self.age, self.gender, self.email, self.id)
                    )
                    if result.rowcount > 0:
                        print(f"User with ID {self.id} updated successfully.")
                    else:
                        print(f"User with ID {self.id} not found.")
        except IntegrityError as e:
            print(f"Error saving user: {e}")
        except ValueError as e:
            print(f"Error: {e}")

    @staticmethod
    def get(email):
        """Retrieve a user by email"""
        try:
            with db.connection_context():
                cursor = db.execute_sql(
                    "SELECT id, first_name, last_name, age, gender, email FROM users WHERE email = ?",
                    (email,)
                )
                row = cursor.fetchone()
                if row:
                    return User(id=row[0], first_name=row[1], last_name=row[2], age=row[3], gender=row[4], email=row[5])
                else:
                    raise ValueError(f"User with email {email} not found.")
        except Exception as e:
            print(f"Error retrieving user: {e}")
            raise

    def delete(self):
        """Delete a user"""
        try:
            with db.connection_context():
                result = db.execute_sql(
                    "DELETE FROM users WHERE id = ?",
                    (self.id,)
                )
                if result.rowcount > 0:
                    print(f"User with ID {self.id} deleted successfully.")
                    self.id = None
                else:
                    print(f"User with ID {self.id} not found.")
        except Exception as e:
            print(f"Error deleting user: {e}")

class Loan(BaseModel):
    table_name = 'loans'
    id = IntegerField(primary_key=True)
    book_id = IntegerField()
    user_id = IntegerField()

    @staticmethod
    def create_table():
        """Create the loans table"""
        try:
            with db.connection_context():
                db.execute_sql("""
                    CREATE TABLE IF NOT EXISTS loans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        book_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY (book_id) REFERENCES books(id),
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """)
            print("Loans table created successfully.")
        except OperationalError as e:
            print(f"Error creating loans table: {e}")

    @staticmethod
    def lend_book(book_id, user_id):
        """Lend a book to a user"""
        try:
            with db.connection_context():
                cursor = db.execute_sql(
                    "SELECT COUNT(*) FROM loans WHERE user_id = ?",
                    (user_id,)
                )
                current_loans = cursor.fetchone()[0]
                if current_loans >= 2:
                    raise ValueError(f"User with ID {user_id} cannot borrow more than two books.")

                cursor = db.execute_sql(
                    "SELECT total_copies, lent_copies FROM books WHERE id = ?",
                    (book_id,)
                )
                book_data = cursor.fetchone()
                if not book_data:
                    raise ValueError(f"Book with ID {book_id} not found.")
                total_copies, lent_copies = book_data
                if lent_copies >= total_copies:
                    raise ValueError(f"No copies of book with ID {book_id} are available.")


                db.execute_sql(
                    "INSERT INTO loans (book_id, user_id) VALUES (?, ?)",
                    (book_id, user_id)
                )

                db.execute_sql(
                    "UPDATE books SET lent_copies = lent_copies + 1 WHERE id = ?",
                    (book_id,)
                )
                print(f"Book with ID {book_id} lent to user with ID {user_id} successfully.")
        except IntegrityError as e:
            print(f"Error lending book: {e}")
        except Exception as e:
            print(f"Error: {e}")

    @staticmethod
    def return_book(book_id, user_id):
        """Return a book"""
        try:
            with db.connection_context():
                result = db.execute_sql(
                    "DELETE FROM loans WHERE book_id = ? AND user_id = ?",
                    (book_id, user_id)
                )
                if result.rowcount > 0:
                    db.execute_sql(
                        "UPDATE books SET lent_copies = lent_copies - 1 WHERE id = ?",
                        (book_id,)
                    )
                    print(f"Book with ID {book_id} returned by user with ID {user_id} successfully.")
                else:
                    print(f"Book with ID {book_id} was not borrowed by user with ID {user_id}.")
        except Exception as e:
            print(f"Error returning book: {e}")

if __name__ == "__main__":
    Book.create_table()
    User.create_table()
    Loan.create_table()

    book1 = Book(title="The Little Prince", author="Antoine de Saint-Exupéry", year=1943, total_copies=3)
    book1.save()
    book2 = Book(title="1984", author="George Orwell", year=1949, total_copies=2)
    book2.save()

    user1 = User(first_name="Ali", last_name="Rezaei", age=20, gender="Male", email="ali@example.com")
    user1.save()
    user2 = User(first_name="Reza", last_name="Mohammadi", age=25, gender="Male", email="reza@example.com")
    user2.save()

    try:
        user3 = User(first_name="Sara", last_name="Ahmadi", age=14, gender="Female", email="sara@example.com")
        user3.save()
    except ValueError as e:
        print(e)

    
    Loan.lend_book(book_id=book1.id, user_id=user1.id)  
    Loan.lend_book(book_id=book1.id, user_id=user2.id)  
    Loan.lend_book(book_id=book2.id, user_id=user1.id)  
    try:
        Loan.lend_book(book_id=book2.id, user_id=user1.id) 
    except ValueError as e:
        print(e)
    try:
        Loan.lend_book(book_id=book1.id, user_id=user1.id) 
    except ValueError as e:
        print(e)

    
    Loan.return_book(book_id=book1.id, user_id=user1.id)
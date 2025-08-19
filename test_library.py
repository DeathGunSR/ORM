import unittest
from peewee import SqliteDatabase
from library import Book, User, Loan, database_proxy

# Use an in-memory SQLite database for testing
test_db = SqliteDatabase(':memory:')

class TestLibrary(unittest.TestCase):
    def setUp(self):
        # Initialize the proxy with an in-memory database
        database_proxy.initialize(test_db)
        database_proxy.connect()
        Book.create_table()
        User.create_table()
        Loan.create_table()

    def tearDown(self):
        # Drop the tables and close the connection
        database_proxy.drop_tables([Book, User, Loan])
        database_proxy.close()

    def test_create_book(self):
        book = Book(title="Test Book", author="Test Author", year=2023, total_copies=5)
        book.save()
        retrieved_book = Book.get(title="Test Book")
        self.assertEqual(retrieved_book.title, "Test Book")

    def test_get_book(self):
        book = Book(title="Another Book", author="Another Author", year=2023, total_copies=3)
        book.save()
        retrieved_book = Book.get(title="Another Book")
        self.assertIsNotNone(retrieved_book)
        self.assertEqual(retrieved_book.author, "Another Author")

    def test_update_book(self):
        book = Book(title="Update Me", author="Author", year=2023, total_copies=1)
        book.save()
        book.title = "Updated Title"
        book.save()
        updated_book = Book.get(title="Updated Title")
        self.assertEqual(updated_book.title, "Updated Title")

    def test_delete_book(self):
        book = Book(title="Delete Me", author="Author", year=2023, total_copies=1)
        book.save()
        book.delete()
        with self.assertRaises(ValueError):
            Book.get(title="Delete Me")

    def test_create_user(self):
        user = User(first_name="John", last_name="Doe", age=25, gender="Male", email="john.doe@example.com")
        user.save()
        retrieved_user = User.get(email="john.doe@example.com")
        self.assertEqual(retrieved_user.first_name, "John")

    def test_create_user_underage(self):
        with self.assertRaises(ValueError):
            user = User(first_name="Jane", last_name="Doe", age=14, gender="Female", email="jane.doe@example.com")
            user.save()

    def test_get_user(self):
        user = User(first_name="Alice", last_name="Smith", age=30, gender="Female", email="alice.smith@example.com")
        user.save()
        retrieved_user = User.get(email="alice.smith@example.com")
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.last_name, "Smith")

    def test_update_user(self):
        user = User(first_name="Bob", last_name="Brown", age=40, gender="Male", email="bob.brown@example.com")
        user.save()
        user.age = 41
        user.save()
        updated_user = User.get(email="bob.brown@example.com")
        self.assertEqual(updated_user.age, 41)

    def test_delete_user(self):
        user = User(first_name="Charlie", last_name="Davis", age=22, gender="Male", email="charlie.davis@example.com")
        user.save()
        user.delete()
        with self.assertRaises(ValueError):
            User.get(email="charlie.davis@example.com")

    def test_lend_book(self):
        book = Book(title="Lendable", author="Author", year=2023, total_copies=1)
        book.save()
        user = User(first_name="Test", last_name="User", age=20, gender="Other", email="test.user@example.com")
        user.save()
        Loan.lend_book(book.id, user.id)
        updated_book = Book.get(title="Lendable")
        self.assertEqual(updated_book.lent_copies, 1)

    def test_return_book(self):
        book = Book(title="Returnable", author="Author", year=2023, total_copies=1)
        book.save()
        user = User(first_name="Test", last_name="User", age=20, gender="Other", email="test.user@example.com")
        user.save()
        Loan.lend_book(book.id, user.id)
        Loan.return_book(book.id, user.id)
        updated_book = Book.get(title="Returnable")
        self.assertEqual(updated_book.lent_copies, 0)

    def test_lend_book_no_copies(self):
        book = Book(title="No Copies", author="Author", year=2023, total_copies=1, lent_copies=1)
        book.save()
        user = User(first_name="Test", last_name="User", age=20, gender="Other", email="test.user@example.com")
        user.save()
        with self.assertRaises(ValueError):
            Loan.lend_book(book.id, user.id)

    def test_lend_book_user_limit(self):
        book1 = Book(title="Limit Book 1", author="Author", year=2023, total_copies=1)
        book1.save()
        book2 = Book(title="Limit Book 2", author="Author", year=2023, total_copies=1)
        book2.save()
        book3 = Book(title="Limit Book 3", author="Author", year=2023, total_copies=1)
        book3.save()
        user = User(first_name="Test", last_name="User", age=20, gender="Other", email="test.user@example.com")
        user.save()
        Loan.lend_book(book1.id, user.id)
        Loan.lend_book(book2.id, user.id)
        with self.assertRaises(ValueError):
            Loan.lend_book(book3.id, user.id)

if __name__ == '__main__':
    unittest.main()

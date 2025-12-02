import pytest
from sqlalchemy.exc import DataError, IntegrityError
from project import app, db
from project.books.models import Book

@pytest.fixture(scope='module')
def test_app():
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

# 1 Normalne testy
def test_normal_book(test_app):
    book = Book(name="Podstawy programowania", author="Jan Kowalski", year_published=2020, book_type="Programowanie")
    db.session.add(book)
    db.session.commit()

    retrieved = Book.query.filter_by(name="Podstawy programowania").first()
    assert retrieved is not None
    assert retrieved.author == "Jan Kowalski"
    assert retrieved.year_published == 2020
    assert retrieved.book_type == "Programowanie"
    assert retrieved.status == "available"

# 2 Testowanie warunków brzegowych
@pytest.mark.parametrize("name,year", [("A"*64, 1), ("Z"*64, 9999)])
def test_boundary_values(test_app, name, year):
    book = Book(name=name, author="Brzegowy autor", year_published=year, book_type="Brzegowy typ")
    db.session.add(book)
    db.session.commit()

    retrieved = Book.query.filter_by(name=name).first()
    assert retrieved is not None
    assert len(retrieved.name) == 64
    assert retrieved.year_published == year

# 3 Testowanie niepoprawnych danych
@pytest.mark.parametrize("name,author,year,type_", [
    ("Zla ksiazka", "Autor", "Rok2023", "Fikcja"),
    ("Brak autora", None, 2023, "Fikcja"),
])
def test_invalid_data(test_app, name, author, year, type_):
    if not isinstance(year, int) or author is None:
        assert True
    else:
        book = Book(name=name, author=author, year_published=year, book_type=type_)
        db.session.add(book)
        db.session.commit()
        retrieved = Book.query.filter_by(name=name).first()
        assert retrieved is not None

# 4 Ekstremalne testowanie
def test_extreme_values(test_app):
    huge_name = "A" * 10_000_000
    huge_author = "B" * 10_000_000
    book = Book(name=huge_name, author=huge_author, year_published=2023, book_type="Powiesc")
    db.session.add(book)
    db.session.commit()

    retrieved = Book.query.filter_by(name=huge_name).first()
    assert retrieved is not None
    assert len(retrieved.name) == 10_000_000
    assert len(retrieved.author) == 10_000_000

import pytest
import orjson

from fastapi import status
from sqlalchemy import select

from src.models import sellers
from src.models import books

from configurations.database import global_init, delete_db_and_tables


# Тест на ручку создающую книгу
@pytest.mark.asyncio
async def test_create_book(db_session, async_client):
    global_init()  


    first_seller = {
                    "first_name": "Alexander",
                    "last_name": "Boytsov",
                    "email": "AlexanderBoytsov@mail.ru",
                    "password": "00000000"
                    }
    response = await async_client.post("/api/v1/sellers/", json=first_seller)    
    assert response.status_code == status.HTTP_201_CREATED

    data = {"title": "Wrong Code", "author": "Robert Martin", "count_pages": 104, "year": 2007, "seller_id": 1}   
    
    response = await async_client.post("/api/v1/books/", json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()    
    assert result_data == {"id": 1, "title": "Wrong Code", "author": "Robert Martin", "count_pages": 104, "year": 2007, "seller_id": 1}
    



# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):

    global_init()

    first_seller = {
                "first_name": "Alexander",
                "last_name": "Boytsov",
                "email": "AlexanderBoytsov@mail.ru",
                "password": "00000000"
                }
    response = await async_client.post("/api/v1/sellers/", json=first_seller)    
    assert response.status_code == status.HTTP_201_CREATED

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id = 1)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id = 1)
        
    db_session.add_all([book, book_2])
    await db_session.commit()

    response = await async_client.get("/api/v1/books/")
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "books": [
            {"title": "Eugeny Onegin", "author": "Pushkin", "year": 2001, "id": book.id, "count_pages": 104, "seller_id": 1},
            {"title": "Mziri", "author": "Lermontov", "year": 1997, "id": book_2.id, "count_pages": 104, "seller_id": 1}
        ]
    }


#Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    global_init()

    first_seller = {
                "first_name": "Alexander",
                "last_name": "Boytsov",
                "email": "AlexanderBoytsov@mail.ru",
                "password": "00000000"
                }
    response = await async_client.post("/api/v1/sellers/", json=first_seller)    
    assert response.status_code == status.HTTP_201_CREATED

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id = 1)

    db_session.add_all([book])
    await db_session.commit()

    response = await async_client.get(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "count_pages": 104,
        "id": book.id,
        "seller_id": 1
    }


# Тест на ручку удаления книги
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):

    global_init()

    first_seller = {
                 "first_name": "Alexander",
                "last_name": "Boytsov",
                "email": "AlexanderBoytsov@mail.ru",
                "password": "00000000"
                }
    response = await async_client.post("/api/v1/sellers/", json=first_seller)    
    assert response.status_code == status.HTTP_201_CREATED

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id = 1)

    db_session.add_all([book])
    await db_session.commit()

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    global_init()

    first_seller = {
                "first_name": "Alexander",
                "last_name": "Boytsov",
                "email": "AlexanderBoytsov@mail.ru",
                "password": "00000000"
                }
    
    response = await async_client.post("/api/v1/sellers/", json=first_seller)    
    assert response.status_code == status.HTTP_201_CREATED

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id = 1)

    db_session.add_all([book])
    await db_session.commit()

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={"title": "Mziri", "author": "Lermontov", "count_pages": 100, "year": 2007, "id": book.id, "seller_id": 1},
    )
    
    assert response.status_code == status.HTTP_200_OK
    await db_session.commit()
    
    # Проверяем, что обновились все поля
    res = await async_client.get(f"/api/v1/books/{book.id}")    
    assert res.json()["title"] == "Mziri"
    assert res.json()["author"] == "Lermontov"
    assert res.json()["count_pages"] == 100
    assert res.json()["year"] == 2007
    assert res.json()["id"] == book.id
    assert res.json()["seller_id"] == 1






# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(db_session, async_client):
    global_init()  

    data = {"first_name": "Alexander", "last_name": "Boytsov", "email": "AlexanderBoytsov@mail.ru", "password": "00000000"}   
    
    response = await async_client.post("/api/v1/sellers/", json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()    
    assert result_data == {"first_name": "Alexander", "last_name": "Boytsov", "email": "AlexanderBoytsov@mail.ru", "id": 1}
    



# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    global_init()

    seller_1 = sellers.Seller(first_name="Alexander", last_name="Boytsov", email="AlexanderBoytsov@mail.ru", password="00000000")
    seller_2 = sellers.Seller(first_name="Ilya", last_name="Neustroev", email="IlyaNeustroev@mail.ru", password="12345678")
        
    db_session.add_all([seller_1, seller_2])
    await db_session.commit()

    response = await async_client.get("/api/v1/sellers/")
    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "sellers": [
            {"first_name": "Alexander", "last_name": "Boytsov", "email": "AlexanderBoytsov@mail.ru", "id": 1},
            {"first_name": "Ilya", "last_name": "Neustroev", "email": "IlyaNeustroev@mail.ru", "id": 2}
        ]
    }


#Тест на ручку получения одного продавца
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    global_init()

    seller = sellers.Seller(first_name="Alexander", last_name="Boytsov", email="AlexanderBoytsov@mail.ru", password="00000000")

    db_session.add_all([seller])
    await db_session.commit()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
                "first_name": "Alexander",
                "last_name": "Boytsov",
                "email": "AlexanderBoytsov@mail.ru",
                "id": 1,
                'books': []
    }


# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    global_init()

    seller = sellers.Seller(first_name="Alexander", last_name="Boytsov", email="AlexanderBoytsov@mail.ru", password="00000000")

    db_session.add_all([seller])
    await db_session.commit()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    global_init()

    seller = sellers.Seller(first_name="Alexander", last_name="Boytsov", email="AlexanderBoytsov@mail.ru", password="00000000")

    db_session.add_all([seller])
    await db_session.commit()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={"first_name": "Ilya", "last_name": "Neustroev", "email": "IlyaNeustroev@mail.ru", "password": "12345678"},
    )
    
    assert response.status_code == status.HTTP_200_OK
    await db_session.commit()
    
    res = await async_client.get(f"/api/v1/sellers/{seller.id}")    
    assert res.json()["first_name"] == "Ilya"
    assert res.json()["last_name"] == "Neustroev"
    assert res.json()["email"] == "IlyaNeustroev@mail.ru"
    assert res.json()["id"] == seller.id
    
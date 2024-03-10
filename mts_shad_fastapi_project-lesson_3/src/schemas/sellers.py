from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

from schemas.books import BaseBook

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller", "ReturnedSellerAndBooks"]


# Базовый класс "Продавцы", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str
  
# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):    
    password: str

    @field_validator("password")  # Валидатор проверяет, что пароль не слишком короткий
    @staticmethod
    def validate_password(val: str):
        if len(val) < 8:
            raise PydanticCustomError("Validation error", "Password is short!")
        return val


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedSeller(BaseSeller):    
    id: int
        

# Класс для возврата массива объектов "Книга"
class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
        

class ReturnedSellerAndBooks(ReturnedSeller):
    books: list[BaseBook]




    
    

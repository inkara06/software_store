from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Optional
import secrets

app = FastAPI()

# Подключение к MongoDB
client = MongoClient("mongodb+srv://pernebekabylaj:pernebekabylaj@cluster0.fu14y.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["laptop_store"]


# Простейшая аутентификация через HTTP Basic (не рекомендуется для продакшена)
security = HTTPBasic()


def create_admin():
    users = db["users"]
    existing_admin = users.find_one({"username": "admin"})
    if not existing_admin:
        users.insert_one({
            "username": "admin",
            "password": "admin"  # В продакшене пароль лучше хэшировать
        })
        print("Администратор создан: login: admin, password: admin")
    else:
        print("Администратор уже существует.")

# Вызываем создание администратора при запуске
create_admin()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    user = db["users"].find_one({"username": credentials.username})
    if not user or not secrets.compare_digest(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Pydantic-модель для ноутбука (добавлено поле image_url)
class Laptop(BaseModel):
    brand: str
    processor_brand: str
    processor_name: str
    ram_gb: int
    ram_type: str
    ssd: int
    hdd: int
    os: str
    price: float
    rating: str
    image_url: Optional[str] = "https://via.placeholder.com/150"

# Модель ответа (с полем _id)
class LaptopResponse(Laptop):
    id: str = Field(..., alias="_id")

    class Config:
        allow_population_by_field_name = True

# CRUD-эндпоинты для ноутбуков

@app.post("/laptops", response_model=LaptopResponse)
def create_laptop(laptop: Laptop, username: str = Depends(get_current_username)):
    """
    Создание нового ноутбука в базе.
    """
    laptops_collection = db["laptops"]
    laptop_dict = laptop.dict()
    result = laptops_collection.insert_one(laptop_dict)
    laptop_dict["_id"] = str(result.inserted_id)
    return laptop_dict

@app.get("/laptops", response_model=List[LaptopResponse])
def get_laptops(username: str = Depends(get_current_username)):
    """
    Получение списка всех ноутбуков.
    """
    laptops_collection = db["laptops"]
    laptops = []
    for item in laptops_collection.find():
        item["_id"] = str(item["_id"])
        laptops.append(item)
    return laptops

@app.get("/laptops/{laptop_id}", response_model=LaptopResponse)
def get_laptop(laptop_id: str, username: str = Depends(get_current_username)):
    """
    Получение конкретного ноутбука по ID.
    """
    laptops_collection = db["laptops"]
    laptop = laptops_collection.find_one({"_id": ObjectId(laptop_id)})
    if not laptop:
        raise HTTPException(status_code=404, detail="Ноутбук не найден")
    laptop["_id"] = str(laptop["_id"])
    return laptop

@app.put("/laptops/{laptop_id}", response_model=LaptopResponse)
def update_laptop(laptop_id: str, laptop: Laptop, username: str = Depends(get_current_username)):
    """
    Обновление данных ноутбука по ID.
    """
    laptops_collection = db["laptops"]
    result = laptops_collection.update_one({"_id": ObjectId(laptop_id)}, {"$set": laptop.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Ноутбук не найден или изменений не внесено")
    updated_laptop = laptops_collection.find_one({"_id": ObjectId(laptop_id)})
    updated_laptop["_id"] = str(updated_laptop["_id"])
    return updated_laptop

@app.delete("/laptops/{laptop_id}")
def delete_laptop(laptop_id: str, username: str = Depends(get_current_username)):
    """
    Удаление ноутбука по ID.
    """
    laptops_collection = db["laptops"]
    result = laptops_collection.delete_one({"_id": ObjectId(laptop_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ноутбук не найден")
    return {"detail": "Ноутбук удалён"}

# Эндпоинты для регистрации и входа пользователей

class User(BaseModel):
    username: str
    password: str

@app.post("/register")
def register_user(user: User):
    if db["users"].find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    user_data = user.dict()
    user_data["role"] = "user"
    db["users"].insert_one(user.dict())
    return {"message": "Пользователь зарегистрирован"}

@app.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Вход пользователя по HTTP Basic аутентификации.
    """
    user = db["users"].find_one({"username": credentials.username})
    if not user or not secrets.compare_digest(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"detail": "Вход выполнен успешно", "role": user.get("role", "user")}

# Новые эндпоинты для заказов

class Order(BaseModel):
    laptop_id: str
    quantity: int

class OrderResponse(Order):
    id: str = Field(..., alias="_id")
    username: str

    class Config:
        allow_population_by_field_name = True

@app.post("/orders", response_model=OrderResponse)
def create_order(order: Order, username: str = Depends(get_current_username)):
    """
    Создание нового заказа.
    """
    orders_collection = db["orders"]
    order_dict = order.dict()
    order_dict["username"] = username
    result = orders_collection.insert_one(order_dict)
    order_dict["_id"] = str(result.inserted_id)
    return order_dict

@app.get("/orders", response_model=List[OrderResponse])
def get_orders(username: str = Depends(get_current_username)):
    """
    Получение заказов для текущего пользователя.
    """
    orders_collection = db["orders"]
    orders = []
    for item in orders_collection.find({"username": username}):
        item["_id"] = str(item["_id"])
        orders.append(item)
    return orders


@app.post("/import_laptops")
def import_laptops(laptops: List[Laptop], username: str = Depends(get_current_username)):
    """
    Импорт списка ноутбуков из CSV в базу данных.
    """
    laptops_collection = db["laptops"]
    result = laptops_collection.insert_many([laptop.dict() for laptop in laptops])
    return {"inserted_count": len(result.inserted_ids)}

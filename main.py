import datetime
from pymongo import MongoClient
import pandas as pd
from bson.objectid import ObjectId

# Подключение к MongoDB
try:
    client = MongoClient("mongodb://localhost:27017/")
    print("Подключение к MongoDB успешно!")
    db = client["laptop_store"]  
except Exception as e:
    print(f"Ошибка подключения: {e}")

# Пример добавления ноутбука
def add_laptop():
    laptops = db["laptops"]
    brand = input("Введите бренд ноутбука: ")
    processor_brand = input("Введите бренд процессора: ")
    processor_name = input("Введите название процессора: ")
    ram_gb = input("Введите объем оперативной памяти (GB): ")
    ram_type = input("Введите тип оперативной памяти: ")
    ssd = input("Введите объем SSD (GB): ")
    hdd = input("Введите объем HDD (GB): ")
    os = input("Введите операционную систему: ")
    price = float(input("Введите цену: "))
    rating = input("Введите рейтинг (например, '4 stars'): ")

    laptop_data = {
        "brand": brand,
        "processor_brand": processor_brand,
        "processor_name": processor_name,
        "ram_gb": ram_gb,
        "ram_type": ram_type,
        "ssd": ssd,
        "hdd": hdd,
        "os": os,
        "price": price,
        "rating": rating
    }
    laptops.insert_one(laptop_data)
    print(f"Ноутбук {brand} добавлен в базу данных.")

# Пример получения всех ноутбуков
def get_all_laptops():
    laptops = db["laptops"]
    print("Список всех ноутбуков:")
    for laptop in laptops.find():
        print(laptop)

# Пример обновления цены
def update_price():
    laptops = db["laptops"]
    obj_id = input("Введите уникальный идентификатор (_id): ")
    new_price = float(input("Введите новую цену: "))
    result = laptops.update_one({"_id": ObjectId(obj_id)}, {"$set": {"price": new_price}})
    if result.modified_count > 0:
        print(f"Цена ноутбука обновлена до {new_price}.")
    else:
        print("Ноутбук не найден или цена не изменилась.")

# Пример удаления ноутбука
def delete_laptop():
    laptops = db["laptops"]
    obj_id = input("Введите уникальный идентификатор (_id): ")
    result = laptops.delete_one({"_id": ObjectId(obj_id)})
    if result.deleted_count > 0:
        print("Ноутбук успешно удалён.")
    else:
        print("Ноутбук не найден.")
        
# Функция для поиска ноутбуков
def find_laptops():
    laptops = db["laptops"]
    obj_id = input("Введите уникальный идентификатор (_id) (оставьте пустым, если не требуется): ").strip()
    brand = input("Введите бренд ноутбука (оставьте пустым, если не требуется): ").strip()
    price_input = input("Введите максимальную цену (оставьте пустым, если не требуется): ").strip()

    query = {}
    if obj_id:
        try:
            query["_id"] = ObjectId(obj_id)
        except Exception as e:
            print("Неверный формат _id.")
            return
    if brand:
        query["brand"] = brand
    if price_input:
        try:
            price = float(price_input)
            query["price"] = {"$lte": price}
        except ValueError:
            print("Цена должна быть числом.")
            return

    results = list(laptops.find(query))
    if results:
        print("Найденные ноутбуки:")
        for laptop in results:
            print(laptop)
    else:
        print("Ноутбуки не найдены.")


# Функция для загрузки данных из CSV
def import_laptops_from_csv(csv_path):
    try:
        # Чтение CSV файла
        data = pd.read_csv(csv_path)
        
        # Проверка наличия необходимых колонок
        required_columns = ["brand", "processor_brand", "processor_name", "ram_gb", "ram_type", "ssd", "hdd", "os", "price", "rating"]
        if not all(col in data.columns for col in required_columns):
            print("Ошибка: CSV файл должен содержать колонки: brand, processor_brand, processor_name, ram_gb, ram_type, ssd, hdd, os, price, rating.")
            return
        
        # Преобразование данных в список словарей
        laptops = db["laptops"]
        laptop_list = data.to_dict(orient="records")
        
        # Вставка данных в MongoDB
        result = laptops.insert_many(laptop_list)
        print(f"Успешно добавлено {len(result.inserted_ids)} записей.")
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")

# Подменю "Настройки товаров"
def product_settings_menu():
    while True:
        print("\nНастройки товаров:")
        print("1. Добавить ноутбук")
        print("2. Обновить цену ноутбука")
        print("3. Удалить ноутбук")
        print("4. Показать все ноутбуки")
        print("5. Загрузить данные из CSV")
        print("6. Поиск ноутбука")
        print("7. Отмена")
        choice = input("Введите номер действия: ")

        if choice == "1":
            add_laptop()
        elif choice == "2":
            update_price()
        elif choice == "3":
            delete_laptop()
        elif choice == "4":
            get_all_laptops()
        elif choice == "5":
            csv_path = input("Введите путь к CSV файлу: ")
            import_laptops_from_csv(csv_path)
        elif choice == "6":
            find_laptops()
        elif choice == "7":
            print("Возврат в главное меню.")
            break
        else:
            print("Неверный выбор, попробуйте снова.")

# Главное меню программы
def main_menu():
    while True:
        print("\nГлавное меню:")
        print("1. Настройки товаров")
        print("2. Посмотреть все ноутбуки")
        print("3. Выход")
        choice = input("Введите номер действия: ")

        if choice == "1":
            product_settings_menu()
        elif choice == "2":
            get_all_laptops()
        elif choice == "3":
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор, попробуйте снова.")

# Запуск программы
main_menu()


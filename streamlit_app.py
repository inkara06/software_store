import streamlit as st
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
import subprocess
import atexit   

backend_process = subprocess.Popen(["uvicorn", "backend:app", "--reload"])

def on_exit():
    backend_process.terminate()
atexit.register(on_exit)

# URL бэкенда (предполагается, что он запущен на localhost:8000)
API_URL = "http://localhost:8000"

st.markdown("<h1 style='text-align: center;'>Laptops Store</h1>", unsafe_allow_html=True)




# Аутентификация пользователя через боковую панель
st.sidebar.header("Аутентификация")
auth_mode = st.sidebar.radio("Выберите действие", ["Войти", "Зарегистрироваться"])

if auth_mode == "Войти":
    username = st.sidebar.text_input("Имя пользователя")
    password = st.sidebar.text_input("Пароль", type="password")
    if st.sidebar.button("Войти") and username and password:
        try:
            response = requests.post(f"{API_URL}/login", auth=HTTPBasicAuth(username, password))
            if response.status_code == 200:
                data = response.json()
                st.sidebar.success("Вход выполнен успешно!")
                st.session_state['auth'] = (username, password)
                st.session_state['role'] = data.get("role", "user")
            else:
                st.sidebar.error("Ошибка входа. Проверьте данные.")
        except Exception as e:
            st.sidebar.error(f"Ошибка подключения: {e}")

            
if auth_mode == "Зарегистрироваться":
            new_username = st.sidebar.text_input("Новое имя пользователя")
            new_password = st.sidebar.text_input("Пароль", type="password")
            confirm_password = st.sidebar.text_input("Подтвердите пароль", type="password")
            if st.sidebar.button("Зарегистрироваться"):
                if new_password == confirm_password:
                    try:
                        response = requests.post(f"{API_URL}/register", json={
                        "username": new_username,
                        "password": new_password
                    })
                        if response.status_code == 200:
                            st.sidebar.success("Пользователь зарегистрирован!")
                        else:
                             st.sidebar.error(f"Ошибка регистрации: {response.json().get('detail', 'Неизвестная ошибка')}")
                    except Exception as e:
                        st.sidebar.error(f"Ошибка запроса: {e}")
            else:
                st.sidebar.error("Пароли не совпадают!")


# Режим доступа: Администратор или Пользователь
if 'auth' in st.session_state:
    role = st.session_state.get('role', 'user')

    if role == 'admin':
        mode = st.sidebar.radio("Режим доступа", ["Администратор", "Пользователь"])
    else:
        mode = "Пользователь"

    st.sidebar.write(f"Вы вошли как: {st.session_state['auth'][0]} ({role})")

    # Показываем интерфейс только после входа
    if mode == "Администратор":
        st.write("Здесь функционал администратора.")
    elif mode == "Пользователь":
        st.write("Здесь функционал пользователя.")

else:
    st.sidebar.info("Пожалуйста, войдите для доступа к функционалу.")


if 'auth' in st.session_state:
    auth = HTTPBasicAuth(*st.session_state['auth'])
    
    # --------------------- РЕЖИМ АДМИНИСТРАТОРА ---------------------
    if mode == "Администратор":
        st.header("Операции с ноутбуками")
        admin_menu = st.selectbox("Выберите операцию", ["Просмотр всех", "Добавить", "Обновить", "Удалить"])
        
        if admin_menu == "Просмотр всех":
            st.subheader("Список ноутбуков")
            try:
                response = requests.get(f"{API_URL}/laptops", auth=auth)
                if response.status_code == 200:
                    laptops = response.json()
                    if laptops:
                        df = pd.DataFrame(laptops)
                        st.dataframe(df)
                    else:
                        st.info("Нет ноутбуков для отображения.")
                else:
                    st.error("Не удалось получить данные.")
            except Exception as e:
                st.error(f"Ошибка запроса: {e}")
        
        elif admin_menu == "Добавить":
            st.subheader("Добавить новый ноутбук")
            brand = st.text_input("Бренд", key="add_brand")
            processor_brand = st.text_input("Бренд процессора", key="add_processor_brand")
            processor_name = st.text_input("Название процессора", key="add_processor_name")
            ram_gb = st.number_input("Оперативная память (GB)", min_value=1, step=1, key="add_ram_gb")
            ram_type = st.text_input("Тип оперативной памяти", key="add_ram_type")
            ssd = st.number_input("Объём SSD (GB)", min_value=1, step=1, key="add_ssd")
            hdd = st.number_input("Объём HDD (GB)", min_value=0, step=1, key="add_hdd")
            os_value = st.text_input("Операционная система", key="add_os")
            price = st.number_input("Цена", min_value=0.0, format="%.2f", key="add_price")
            rating = st.text_input("Рейтинг", key="add_rating")
            image_url = st.text_input("URL изображения", key="add_image_url", value="https://via.placeholder.com/150")
            
            # Блок загрузки файла CSV
            st.subheader("Импорт из CSV-файла")
            uploaded_file = st.file_uploader("Загрузите CSV-файл с ноутбуками", type=["csv"])

            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.write("Загруженные данные:")
                    st.dataframe(df)

                    if st.button("Импортировать данные из CSV"):
                        try:
                            # Отправляем весь CSV одним запросом
                            response = requests.post(
                            f"{API_URL}/import_laptops",
                            json=df.to_dict(orient="records"),
                            auth=auth
                            )

                            if response.status_code == 200:
                                st.success(f"Импортировано {response.json()['inserted_count']} ноутбуков!")
                            else:
                                st.error(f"Ошибка импорта: {response.json().get('detail', 'Неизвестная ошибка')}")
                        except Exception as e:
                            st.error(f"Ошибка подключения: {e}")
                except Exception as e:
                    st.error(f"Ошибка чтения файла: {e}")
            
            if st.button("Добавить ноутбук", key="add_button"):
                laptop_data = {
                    "brand": brand,
                    "processor_brand": processor_brand,
                    "processor_name": processor_name,
                    "ram_gb": int(ram_gb),
                    "ram_type": ram_type,
                    "ssd": int(ssd),
                    "hdd": int(hdd),
                    "os": os_value,
                    "price": float(price),
                    "rating": rating,
                    "image_url": image_url
                }
                try:
                    response = requests.post(f"{API_URL}/laptops", json=laptop_data, auth=auth)
                    if response.status_code in (200, 201):
                        st.success("Ноутбук успешно добавлен!")
                    else:
                        st.error("Ошибка при добавлении ноутбука.")
                except Exception as e:
                    st.error(f"Ошибка запроса: {e}")
                    
            
                    
            
                    
        
        
        elif admin_menu == "Обновить":
            st.subheader("Обновить данные ноутбука")
            laptop_id = st.text_input("ID ноутбука для обновления", key="update_id")
            new_price = st.number_input("Новая цена", min_value=0.0, format="%.2f", key="update_price")
            if st.button("Обновить ноутбук", key="update_button"):
                if laptop_id:
                    try:
                        get_response = requests.get(f"{API_URL}/laptops/{laptop_id}", auth=auth)
                        if get_response.status_code == 200:
                            laptop = get_response.json()
                            laptop["price"] = float(new_price)
                            response = requests.put(f"{API_URL}/laptops/{laptop_id}", json=laptop, auth=auth)
                            if response.status_code == 200:
                                st.success("Ноутбук успешно обновлён!")
                            else:
                                st.error("Ошибка при обновлении ноутбука.")
                        else:
                            st.error("Ноутбук с данным ID не найден.")
                    except Exception as e:
                        st.error(f"Ошибка запроса: {e}")
                else:
                    st.error("Пожалуйста, введите ID ноутбука для обновления.")
        
        elif admin_menu == "Удалить":
            st.subheader("Удалить ноутбук")
            laptop_id = st.text_input("ID ноутбука для удаления", key="delete_id")
            if st.button("Удалить ноутбук", key="delete_button"):
                if laptop_id:
                    try:
                        response = requests.delete(f"{API_URL}/laptops/{laptop_id}", auth=auth)
                        if response.status_code == 200:
                            st.success("Ноутбук успешно удалён!")
                        else:
                            st.error("Ошибка при удалении ноутбука.")
                    except Exception as e:
                        st.error(f"Ошибка запроса: {e}")
                else:
                    st.error("Пожалуйста, введите ID ноутбука для удаления.")
    
    # --------------------- РЕЖИМ ПОЛЬЗОВАТЕЛЯ ---------------------
    elif mode == "Пользователь":
        st.header("Пользовательский режим")
        user_menu = st.selectbox("Выберите опцию", ["Каталог ноутбуков", "Мои заказы"])
        
        # ---- Каталог ----
        if user_menu == "Каталог ноутбуков":
            st.subheader("Поиск ноутбуков 🔍")

            # Форма поиска
            search_brand = st.text_input("Бренд (можно частично)", key="search_brand")
            min_price = st.number_input("Минимальная цена", min_value=0.0, format="%.2f", key="min_price")
            max_price = st.number_input("Максимальная цена", min_value=0.0, format="%.2f", key="max_price")
            min_rating = st.number_input("Минимальный рейтинг (от 0 до 5)", min_value=0.0, max_value=5.0, step=0.1, key="min_rating")

            if st.button("Найти ноутбуки"):
                try:
                    search_params = {
                        "brand": search_brand if search_brand else None,
                        "min_price": min_price if min_price > 0 else None,
                        "max_price": max_price if max_price > 0 else None,
                        "min_rating": min_rating if min_rating > 0 else None
                        }
                    search_params = {k: v for k, v in search_params.items() if v is not None}  # Удаляем пустые фильтры

                    response = requests.get(f"{API_URL}/search_laptops", params=search_params, auth=auth)
                    if response.status_code == 200:
                        laptops = response.json()
                        if laptops:
                            st.write(f"Найдено {len(laptops)} ноутбуков:")
                            for laptop in laptops:
                                col1, col2 = st.columns([1, 3])  
                                with col1:
                                    st.image(laptop.get("image_url", "https://via.placeholder.com/150"), width=150)
                                with col2:
                                    st.markdown(f"**{laptop['brand']} {laptop['processor_name']}**")
                                    st.text(f"Цена: {laptop['price']}")
                                    st.text(f"Рейтинг: {laptop['rating']}")

                                    # Поле для ввода количества и кнопка "Заказать"
                                    quantity = st.number_input("Количество", min_value=1, step=1, key=f"qty_{laptop['_id']}")
                                    if st.button("Заказать", key=f"order_{laptop['_id']}"):
                                        order_data = {
                                            "laptop_id": laptop["_id"],
                                            "quantity": int(quantity)
                                            }
                                        try:
                                                order_response = requests.post(f"{API_URL}/orders", json=order_data, auth=auth)
                                                if order_response.status_code in (200, 201):
                                                    st.success("Заказ успешно оформлен!")
                                                else:
                                                    st.error("Ошибка при оформлении заказа.")
                                        except Exception as e:
                                                st.error(f"Ошибка запроса: {e}")

                                        st.markdown("---")  # Разделитель между ноутбуками
                                    else:
                                        st.warning("Ничего не найдено по этим критериям.")
                            else:
                                st.error("Ошибка при поиске.")
                except Exception as e:
                    st.error(f"Ошибка подключения: {e}")

                
            try:
                response = requests.get(f"{API_URL}/laptops", auth=auth)
                if response.status_code == 200:
                    laptops = response.json()
                    if laptops:
                        num_cols = 3
                        for i in range(0, len(laptops), num_cols):
                            cols = st.columns(num_cols)
                            for idx, laptop in enumerate(laptops[i:i+num_cols]):
                                with cols[idx]:
                                    image_url = laptop.get("image_url", "https://via.placeholder.com/150")
                                    st.image(image_url, use_container_width=True)
                                    st.markdown(f"**{laptop['brand']} {laptop['processor_name']}**")
                                    st.text(f"Цена: {laptop['price']}")
                                    st.text(f"Рейтинг: {laptop['rating']}")
                                    quantity = st.number_input("Количество", min_value=1, step=1, key=f"qty_{laptop['_id']}")
                                    if st.button("Заказать", key=f"order_{laptop['_id']}"):
                                        order_data = {
                                            "laptop_id": laptop["_id"],
                                            "quantity": int(quantity)
                                        }
                                        try:
                                            order_response = requests.post(f"{API_URL}/orders", json=order_data, auth=auth)
                                            if order_response.status_code in (200, 201):
                                                st.success("Заказ успешно оформлен!")
                                            else:
                                                st.error("Ошибка при оформлении заказа.")
                                        except Exception as e:
                                            st.error(f"Ошибка запроса: {e}")
                    else:
                        st.info("Нет ноутбуков для отображения.")
                else:
                    st.error("Не удалось получить данные.")
            except Exception as e:
                st.error(f"Ошибка запроса: {e}")
        
        # ---- Мои заказы ----
        elif user_menu == "Мои заказы":
            st.subheader("Мои заказы")
            try:
                response = requests.get(f"{API_URL}/orders", auth=auth)
                if response.status_code == 200:
                    orders = response.json()
                    if orders:
                        total_sum = 0
                        for order in orders:
                        # Получаем информацию о ноутбуке
                            laptop_id = order["laptop_id"]
                            laptop_response = requests.get(f"{API_URL}/laptops/{laptop_id}", auth=auth)
                    
                            if laptop_response.status_code == 200:
                                laptop = laptop_response.json()
                        
                                col1, col2, col3 = st.columns([1, 3, 1])  # Разделяем блок на 3 части

                                with col1:
                                    st.image(laptop.get("image_url", "https://via.placeholder.com/150"), width=120)

                                with col2:
                                    st.markdown(f"**{laptop['brand']} {laptop['processor_name']}**")
                                    st.text(f"Цена за штуку: {laptop['price']} KZT")
                                    st.text(f"Количество: {order['quantity']}")
                                    cost = laptop['price'] * order['quantity']
                            
                                with col3:
                                    if st.button("❌ Удалить", key=f"del_{order['_id']}"):
                                        delete_response = requests.delete(f"{API_URL}/orders/{order['_id']}", auth=auth)
                                        if delete_response.status_code == 200:
                                            st.success("Заказ успешно удалён!")
                                        else:
                                            st.error("Ошибка при удалении заказа.")

                                        st.markdown("---")  # Разделитель между заказами
                                        total_sum += cost
                    
                                total_sum += cost
                            else:
                                st.error("Ошибка при получении данных ноутбука.")
                        
                        st.markdown(f"### Общая сумма: {total_sum} KZT")
                    else:
                        st.info("У вас пока нет заказов.")
                else:
                    st.error("Ошибка при получении заказов.")
            except Exception as e:
                st.error(f"Ошибка запроса: {e}")

                

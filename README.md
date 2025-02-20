# Laptop Store Application

## Description
Laptop Store is a web application that allows you to manage laptop data, place orders, and register users with different access levels (user, administrator). The application is built using MongoDB, FastAPI, and Streamlit.

## Key Features
- User registration (default role - user).
- Authentication via HTTP Basic.
- CRUD operations with laptops (for admin only).
- Viewing laptop catalog and placing orders (for users).
- Viewing order history (for users).

## Technologies Used
- Backend: FastAPI
- Frontend: Streamlit
- Database: MongoDB Atlas (NoSQL)

## Installation and Launch

### 1. Clone the Repository
```bash
git clone <repository_link>
cd laptop_store
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run streamlit_app.py
```

Running `streamlit_app.py` will automatically start the FastAPI backend server.

## MongoDB Atlas Connection Setup

Open the `backend.py` file and edit the connection string:
```python
client = MongoClient("mongodb+srv://<username>:<password>@cluster0.fu14y.mongodb.net/?retryWrites=true&w=majority")
```
Replace `<username>` and `<password>` with your MongoDB Atlas credentials.

## Project Structure
```
.
├── backend.py         # FastAPI backend
├── streamlit_app.py   # Streamlit frontend
├── main.py            # Console-based application (optional)
└── requirements.txt   # Dependencies
```

## API Endpoints (FastAPI)
- `POST /register` - Register a user
- `POST /login` - User login
- `GET /laptops` - Get a list of laptops
- `POST /laptops` - Add a laptop
- `PUT /laptops/{id}` - Update a laptop
- `DELETE /laptops/{id}` - Delete a laptop
- `POST /orders` - Create an order
- `GET /orders` - Get orders

## Requirements
- Python 3.10+
- Streamlit
- FastAPI
- Uvicorn
- Pymongo
- Pandas

## Authors
- Inkara
- Abylay
- Sanzhar
  


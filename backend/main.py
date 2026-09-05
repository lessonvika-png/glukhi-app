from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

from models import User, SessionLocal

app = FastAPI()

# Дозволяємо фронтенду (сайту) звертатись до цього бекенду.
# Поки що дозволяємо все ("*") для зручності розробки — коли сайт буде на постійному
# домені, тут варто буде вказати конкретну адресу замість "*", для безпеки.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Ця функція дає доступ до бази даних під час одного запиту і закриває з'єднання після
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Опис того, які дані очікуємо отримати від форми реєстрації
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "korystuvach"


# Опис того, які дані очікуємо отримати від форми входу
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@app.get("/")
def read_root():
    return {"message": "Привіт! Бекенд працює."}


@app.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Перевіряємо, чи вже є користувач з таким email
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Користувач з таким email вже існує")

    hashed_password = pwd_context.hash(data.password)

    new_user = User(
        name=data.name,
        email=data.email,
        hashed_password=hashed_password,
        role=data.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role,
    }


@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Шукаємо користувача за email
    user = db.query(User).filter(User.email == data.email).first()

    # Якщо користувача нема АБО пароль не співпадає — та сама помилка для обох випадків.
    # Це навмисно: якщо казати окремо "нема такого email" і "неправильний пароль",
    # зловмисник міг би визначити, які email взагалі зареєстровані.
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неправильний email або пароль")

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }
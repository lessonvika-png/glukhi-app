import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

from models import User, Recording, SessionLocal
from youtube_upload import upload_video_bytes

app = FastAPI()

# Секретний ключ, яким підписуються токени — це "секретна печатка", яка підтверджує,
# що токен видав саме наш сервер, а не хтось інший. Читається з .env / змінних середовища.
# Якщо не задано — використовується запасний варіант (нормально для розробки,
# але для продакшену варто задати власний SECRET_KEY в .env і на Render).
SECRET_KEY = os.getenv("SECRET_KEY", "тимчасовий-ключ-для-розробки-заміни-мене")
ALGORITHM = "HS256"
TOKEN_LIFETIME_DAYS = 30

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


# Створює токен-перепустку для конкретного користувача, дійсний 30 днів
def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=TOKEN_LIFETIME_DAYS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Ця функція перевіряє токен, який прийшов у заголовку запиту, і повертає користувача.
# Якщо токена нема, він застарів, чи підроблений — повертає помилку 401.
def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Потрібен вхід у систему")

    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Сесія застаріла, увійди знову")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Недійсний токен")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Користувача не знайдено")
    return user


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

    token = create_access_token(new_user.id)

    return {
        "access_token": token,
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

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }


@app.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }


@app.post("/recordings")
def create_recording(
    word: str = Form(...),
    video: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Приймає відео від перекладача, завантажує його на YouTube (unlisted),
    і зберігає запис у базі даних зі статусом "на розгляді".
    """
    video_bytes = video.file.read()

    try:
        youtube_video_id = upload_video_bytes(video_bytes, title=word)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Не вдалось завантажити відео: {e}")

    new_recording = Recording(
        word=word,
        youtube_video_id=youtube_video_id,
        translator_id=current_user.id,
        status="pending",
    )
    db.add(new_recording)
    db.commit()
    db.refresh(new_recording)

    return {
        "id": new_recording.id,
        "word": new_recording.word,
        "youtube_video_id": new_recording.youtube_video_id,
        "status": new_recording.status,
    }


@app.get("/recordings/me")
def list_my_recordings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Повертає всі записи поточного перекладача — для показу в його кабінеті."""
    recordings = db.query(Recording).filter(Recording.translator_id == current_user.id).order_by(Recording.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "word": r.word,
            "youtube_video_id": r.youtube_video_id,
            "status": r.status,
        }
        for r in recordings
    ]
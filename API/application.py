from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ChessAI.API.database import database
from ChessAI.API.database.db_models import Base
app = FastAPI()
# Это создаст все таблицы, если они не существуют
Base.metadata.create_all(bind=database.engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или указать конкретные домены, например, ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все HTTP методы
    allow_headers=["*"],  # Разрешить все заголовки
)

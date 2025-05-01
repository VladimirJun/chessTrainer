from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# URL для подключения к базе данных
DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/ChessAPI"

# Движок для взаимодействия с базой данных
engine = create_engine(DATABASE_URL)

# Сессия для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
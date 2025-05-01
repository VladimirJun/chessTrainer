
#файл, в котором происходит непосредственно запуск сервера (server.py - как рудимент, исправлю в ближайшем будущем)
# Добавляем корневой путь проекта в sys.path
import sys
import os
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)
import logging
from controllers import player_controller, match_controller
from application import app
from controllers.assistant_controller import router as assistant_router
from API.controllers.evaluation_controller import router as evaluation_router



app.include_router(player_controller.router, prefix="/api")
app.include_router(match_controller.router, prefix="/api")
app.include_router(evaluation_router)

app.include_router(assistant_router, prefix="/api/assistant", tags=["Assistant"])


@app.get("/")
def read_root():
    return {"Welcome to Chess Trainer API"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
log_file = "ServerLog.log"
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[
                        logging.FileHandler(log_file),
                        logging.StreamHandler()
                    ])


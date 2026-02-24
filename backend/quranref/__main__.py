import uvicorn

from .main import DEV_PORT

uvicorn.run("quranref.main:app", host="127.0.0.1", port=DEV_PORT, reload=True)

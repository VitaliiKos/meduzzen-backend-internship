import uvicorn
from config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run("main:app", host=settings.app_host, port=settings.app_port, reload=True)

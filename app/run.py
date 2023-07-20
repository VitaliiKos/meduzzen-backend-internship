import uvicorn
from config import settings

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=settings.app_port, reload=True)

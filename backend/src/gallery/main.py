import uvicorn
from backend.src.gallery import config

if __name__ == "__main__":
    uvicorn.run("src.app:app", **config.UVICORN)

import uvicorn
from gallery import config

if __name__ == "__main__":
    uvicorn.run("gallery.app:app", **config.UVICORN)

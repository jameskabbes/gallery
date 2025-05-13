import uvicorn
import config

if __name__ == "__main__":
    uvicorn.run("app:app", **config.UVICORN)

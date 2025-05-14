import uvicorn
from arbor_imago import config

if __name__ == "__main__":
    uvicorn.run("arbor_imago.app:app", **config.UVICORN)

import uvicorn
from fastapi import FastAPI

from api.routes.auth_routes import router as auth_router
from middlewares.cors import setup_cors

app = FastAPI()
setup_cors(app)
app.include_router(auth_router, tags=["auth"])

if __name__ == "__main__":
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)

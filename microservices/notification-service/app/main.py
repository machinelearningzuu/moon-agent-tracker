import uvicorn
from fastapi import FastAPI
from .routes import router as notif_router

app = FastAPI(title="Notification Service")
app.include_router(notif_router, prefix="/notifications")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
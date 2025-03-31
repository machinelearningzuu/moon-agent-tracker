import uvicorn
from fastapi import FastAPI
from .routes import router as agent_router

app = FastAPI(title="Agent Service")
app.include_router(agent_router, prefix="/agents")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
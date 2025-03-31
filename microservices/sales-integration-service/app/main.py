import uvicorn
from fastapi import FastAPI
from .routes import router as sales_router

app = FastAPI(title="Sales Integration Service")
app.include_router(sales_router, prefix="/sales")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
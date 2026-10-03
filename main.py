from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.rooms import router as rooms_router
from routers.upload import router as upload_router
from routers.chat import router as chat_router

from services.qdrant import create_collection

app = FastAPI(title="E-commerce & Retail (Multimodal RAG Platform )")

app.include_router(auth_router)
app.include_router(rooms_router)
app.include_router(upload_router)
app.include_router(chat_router)

@app.on_event("startup")
def startup_event():
    create_collection()


@app.get("/")
def root():
    return {"message": "Multimodal RAG API is running"}
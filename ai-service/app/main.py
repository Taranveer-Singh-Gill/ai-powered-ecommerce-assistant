from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.products import router as products_router
from app.api.chat import router as chat_router


app = FastAPI(
    title="Commerce AI Assistant API",
    description="AI assistant service for the e-commerce storefront.",
    version="0.1.0",
)

app.include_router(products_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ai-powered-ecommerce-assistant-frontend.onrender.com",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "commerce-ai-assistant"
    }
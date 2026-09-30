from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from app.services.ai_service import (
    generate_response,
    generate_product_recommendation,
    rerank_products,
)
from app.services.intent_service import (
    ShoppingIntent,
    extract_shopping_intent,
)
from app.services.vector_service import search_filtered_products

router = APIRouter(
    prefix="/chat",
    tags=["AI Assistant"]
)


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=1000,
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty.")

        return value

@router.post("")
async def chat(request: ChatRequest):
    response = await generate_response(request.message)

    return {
        "message": request.message,
        "response": response
    }
@router.post("/intent", response_model=ShoppingIntent)
async def get_shopping_intent(request: ChatRequest):
    return await extract_shopping_intent(request.message)

@router.post("/recommend")
async def recommend_products(request: ChatRequest):
    try:
        # Step 1: Understand the customer's request.
        intent = await extract_shopping_intent(request.message)

        # Step 2: Retrieve and filter semantically relevant products.
        products = await search_filtered_products(
            query=intent.search_query or request.message,
            category=intent.category,
            max_price=intent.max_price,
            min_rating=intent.min_rating,
        )

        # Step 3: Rerank products based on the customer's request.
        products = await rerank_products(
            message=request.message,
            products=products,
            limit=5,
        )

        # Step 4: Select only the fields needed by the frontend.
        recommendations = [
            {
                "id": product["id"],
                "title": product["title"],
                "brand": product.get("brand"),
                "price": product["price"],
                "rating": product["rating"],
                "stock": product["stock"],
                "description": product.get("description"),
                "thumbnail": product.get("thumbnail"),
            }
            for product in products[:5]
        ]

        # Step 5: Generate a grounded AI response.
        ai_response = await generate_product_recommendation(
            request.message,
            recommendations,
        )

        # Step 6: Return the response and matching products.
        return {
            "message": request.message,
            "intent": intent.model_dump(),
            "response": ai_response,
            "count": len(products),
            "products": recommendations,
        }

    except Exception as error:
        print(f"Recommendation error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to generate product recommendations right now.",
        )
from fastapi import APIRouter
from app.services.product_service import get_products, search_products

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get("")
async def list_products(limit: int = 30):
    products = await get_products(limit)

    return {
        "count": len(products),
        "products": products
    }


@router.get("/search")
async def search_product_catalog(q: str, limit: int = 10):
    products = await search_products(q, limit)

    return {
        "query": q,
        "count": len(products),
        "products": products
    }
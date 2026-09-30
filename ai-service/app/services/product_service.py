import httpx

PRODUCTS_URL = "https://dummyjson.com/products"


async def get_products(limit: int = 30):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            PRODUCTS_URL,
            params={"limit": limit}
        )

        response.raise_for_status()

        data = response.json()

        return data["products"]
    
async def search_products(query: str, limit: int = 10):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PRODUCTS_URL}/search",
            params={
                "q": query,
                "limit": limit
            }
        )

    response.raise_for_status()

    data = response.json()

    return data["products"]

async def filter_products(
    in_stock: bool = True,
    category: str | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    search_query: str | None = None,
):
    # Retrieve the product catalog.
    products = await get_products(limit=0)

    # Filter by category.
    if category:
        products = [
            product for product in products
            if product["category"].lower() == category.lower()
        ]

    # Filter by maximum price.
    if max_price is not None:
        products = [
            product for product in products
            if product["price"] <= max_price
        ]

    # Filter by minimum rating.
    if min_rating is not None:
        products = [
            product for product in products
            if product["rating"] >= min_rating
        ]

    # Filter by product name or description.
    if search_query:
        query = search_query.lower()

        products = [
            product for product in products
            if query in product["title"].lower()
            or query in product.get("description", "").lower()
        ]
    
    # Exclude unavailable products by default.
    if in_stock:
        products = [
            product for product in products
            if product.get("stock", 0) > 0
        ]

    return products
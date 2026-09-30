import chromadb
from app.services.product_service import get_products


# Store the vector database locally
client = chromadb.PersistentClient(path="./chroma_db")

# Create the collection if it doesn't exist
collection = client.get_or_create_collection(
    name="products"
)


async def index_products():
    products = await get_products(limit=0)

    ids = []
    documents = []
    metadatas = []

    for product in products:
        ids.append(str(product["id"]))

        documents.append(
            f"Product: {product['title']}. "
            f"Category: {product['category']}. "
            f"Description: {product['description']}"
        )

        metadatas.append({
            "product_id": product["id"],
            "title": product["title"],
            "category": product["category"],
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    return len(products)

def semantic_search(query: str, limit: int = 5):
    results = collection.query(
        query_texts=[query],
        n_results=min(limit, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    return [
        {
            "product_id": metadata["product_id"],
            "title": metadata["title"],
            "category": metadata["category"],
            "description": document,
            "distance": distance,
        }
        for metadata, document, distance in zip(
            results["metadatas"][0],
            results["documents"][0],
            results["distances"][0],
        )
    ]

async def get_semantic_products(query: str, limit: int = 20):
    matches = semantic_search(query, limit=limit)

    products = await get_products(limit=0)

    products_by_id = {
        product["id"]: product
        for product in products
    }

    semantic_products = []

    for match in matches:
        product = products_by_id.get(match["product_id"])

        if product:
            product = product.copy()
            product["_semantic_distance"] = match["distance"]
            semantic_products.append(product)

    return semantic_products

async def search_filtered_products(
    query: str,
    category: str | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    limit: int = 50,
):
    products = await get_semantic_products(
        query=query,
        limit=limit,
    )

    filtered = []

    for product in products:
        if category is not None:
            normalized_category = category.strip().lower()

            category_aliases = {
                "smartphone": "smartphones",
                "phone": "smartphones",
                "mobile phone": "smartphones",
                "laptop": "laptops",
            }

            normalized_category = category_aliases.get(
                normalized_category,
                normalized_category,
            )

            if product["category"].lower() != normalized_category:
                continue

        if max_price is not None:
            if product["price"] > max_price:
                continue

        if min_rating is not None:
            if product["rating"] < min_rating:
                continue

        if product.get("stock", 0) <= 0:
            continue

        filtered.append(product)

    return filtered
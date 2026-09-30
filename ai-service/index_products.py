import asyncio

from app.services.vector_service import index_products


async def main():
    count = await index_products()
    print(f"Successfully indexed {count} products in ChromaDB.")


if __name__ == "__main__":
    asyncio.run(main())
import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel


class ProductRanking(BaseModel):
    product_ids: list[int]

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


async def generate_response(message: str) -> str:
    response = await client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "You are a helpful AI shopping assistant for an "
            "e-commerce website. Give clear, concise answers. "
            "Do not invent product prices, stock, or availability."
        ),
        input=message,
    )

    return response.output_text

async def generate_product_recommendation(
    message: str,
    products: list[dict]
) -> str:

    if not products:
        return (
            "I couldn't find any available products matching "
            "your preferences. Try adjusting your budget or requirements."
        )

    product_context = json.dumps(products, indent=2)

    response = await client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "You are a concise AI shopping assistant for an e-commerce website. "
            "Use ONLY the provided product catalog information. "
            "The website displays the recommended products as visual cards below your response. "
            "Do NOT list products individually. "
            "Do NOT use bullet points, numbered lists, Markdown, links, or image URLs. "
            "Do NOT repeat product prices, ratings, stock counts, or thumbnails. "
            "Give a short conversational summary of why the recommendations match the customer's request. "
            "Mention at most 2 or 3 product names only when useful. "
            "Prioritize products whose descriptions explicitly support the customer's requested features. "
            "Do not infer camera quality, performance, or other specifications from product names, "
            "brands, prices, or ratings alone. "
            "If the provided information does not establish a requested feature, say so briefly. "
            "Keep the response to 2-3 sentences."
        ),
        input=(
            f"Customer request: {message}\n\n"
            f"Available products:\n{product_context}"
        ),
    )

    return response.output_text

async def rerank_products(
    message: str,
    products: list[dict],
    limit: int = 5,
) -> list[dict]:
    if not products:
        return []

    product_context = [
        {
            "id": product["id"],
            "title": product["title"],
            "category": product["category"],
            "price": product["price"],
            "rating": product["rating"],
            "description": product["description"],
        }
        for product in products
    ]

    response = await client.responses.parse(
        model="gpt-4.1-mini",
        instructions=(
            "Select the products that best match the customer's request. "
            "Use ONLY the provided catalog information. "
            "Prioritize products whose descriptions explicitly support "
            "the features requested by the customer. "
            "Do not infer features from brand, product name, price, or rating. "
            f"Return at most {limit} product IDs, ordered from most relevant "
            "to least relevant. Only return IDs from the provided products."
        ),
        input=(
            f"Customer request: {message}\n\n"
            f"Candidate products: {json.dumps(product_context, indent=2)}"
        ),
        text_format=ProductRanking,
    )

    ranked_ids = response.output_parsed.product_ids[:limit]

    products_by_id = {
        product["id"]: product
        for product in products
    }

    return [
        products_by_id[product_id]
        for product_id in ranked_ids
        if product_id in products_by_id
    ]
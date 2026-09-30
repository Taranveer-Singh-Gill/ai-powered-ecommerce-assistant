import os

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


class ShoppingIntent(BaseModel):
    category: str | None
    max_price: float | None
    min_rating: float | None
    search_query: str | None


async def extract_shopping_intent(message: str) -> ShoppingIntent:

    response = await client.responses.parse(
        model="gpt-4.1-mini",
        instructions=(
            "Extract shopping preferences from the customer's message. "
            "Return the product category, maximum price, minimum rating, "
            "and product search query when specified. "
            "Use null for information that is not provided. "
            "Do not invent shopping preferences."
        ),
        input=message,
        text_format=ShoppingIntent,
    )

    return response.output_parsed
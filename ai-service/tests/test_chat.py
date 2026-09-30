from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_empty_message():
    response = client.post(
        "/chat/recommend",
        json={"message": ""},
    )

    assert response.status_code == 422


def test_whitespace_message():
    response = client.post(
        "/chat/recommend",
        json={"message": "   "},
    )

    assert response.status_code == 422

def test_recommend_products(monkeypatch):
    async def mock_extract_intent(message):
        from app.services.intent_service import ShoppingIntent

        return ShoppingIntent(
            category="smartphones",
            max_price=500,
            min_rating=4,
            search_query="good camera",
        )

    async def mock_search_products(**kwargs):
        return [
            {
                "id": 130,
                "title": "Realme XT",
                "brand": "Realme",
                "category": "smartphones",
                "price": 349.99,
                "rating": 4.58,
                "stock": 80,
                "description": "Smartphone focused on camera technology.",
                "thumbnail": "test-image.webp",
            }
        ]

    async def mock_rerank(message, products, limit):
        return products

    async def mock_generate(message, products):
        return "The Realme XT matches your requirements."

    monkeypatch.setattr(
        "app.api.chat.extract_shopping_intent",
        mock_extract_intent,
    )

    monkeypatch.setattr(
        "app.api.chat.search_filtered_products",
        mock_search_products,
    )

    monkeypatch.setattr(
        "app.api.chat.rerank_products",
        mock_rerank,
    )

    monkeypatch.setattr(
        "app.api.chat.generate_product_recommendation",
        mock_generate,
    )

    response = client.post(
        "/chat/recommend",
        json={
            "message": "I need a smartphone with a good camera under $500"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 1
    assert len(data["products"]) == 1
    assert data["products"][0]["title"] == "Realme XT"
    assert data["products"][0]["price"] == 349.99
    assert data["response"] == "The Realme XT matches your requirements."
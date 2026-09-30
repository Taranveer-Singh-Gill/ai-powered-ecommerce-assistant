const AI_API_URL =
  import.meta.env.VITE_AI_API_URL || "http://127.0.0.1:8000";
  
export interface ProductRecommendation {
  id: number;
  title: string;
  brand?: string;
  price: number;
  rating: number;
  stock: number;
  description?: string;
  thumbnail?: string;
}

export interface AIRecommendationResponse {
  message: string;
  response: string;
  count: number;
  products: ProductRecommendation[];
}

export async function getAIRecommendations(
  message: string
): Promise<AIRecommendationResponse> {
  const response = await fetch(`${AI_API_URL}/chat/recommend`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error(
      `AI request failed with status ${response.status}`
    );
  }

  return response.json();
}
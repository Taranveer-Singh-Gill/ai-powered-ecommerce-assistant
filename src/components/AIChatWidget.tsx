import { useState } from "react";
import { getAIRecommendations } from "../aiApi";

import type { ProductRecommendation } from "../aiApi";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  products?: ProductRecommendation[];
}

export default function AIChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    const message = input.trim();

    if (!message || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", content: message },
    ]);

    setInput("");
    setLoading(true);

    try {
      const result = await getAIRecommendations(message);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: result.response,
          products: result.products,
        },
      ]);
    } catch {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {isOpen && (
        <div className="mb-4 flex h-[450px] w-[350px] flex-col overflow-hidden rounded-xl border border-gray-200 bg-white shadow-2xl">
          {/* Header */}
          <div className="bg-blue-600 p-4 text-white">
            <h3 className="font-semibold">Ask Shop AI</h3>
            <p className="text-xs">Your AI shopping assistant</p>
          </div>

          {/* Messages */}
          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {messages.length === 0 && (
              <p className="text-sm text-gray-500">
                Hi! What are you shopping for today?
              </p>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`rounded-lg p-3 text-sm ${
                  message.role === "user"
                    ? "ml-8 bg-blue-100 text-gray-900"
                    : "mr-8 bg-gray-100 text-gray-900"
                }`}
              >
                <>
                <p className="whitespace-pre-wrap">
                    {message.content}
                </p>

                {message.products && message.products.length > 0 && (
                    <div className="mt-4 space-y-3">
                    {message.products.map((product) => (
                        <a
                        key={product.id}
                        href={`/product/${product.id}`}
                        className="flex gap-3 rounded-lg border border-gray-200 bg-white p-3 hover:border-blue-500"
                        >
                        {product.thumbnail && (
                            <img
                            src={product.thumbnail}
                            alt={product.title}
                            className="h-20 w-20 shrink-0 rounded-md object-contain"
                            />
                        )}

                        <div className="min-w-0">
                            <p className="font-semibold text-gray-900">
                            {product.title}
                            </p>

                            <p className="font-medium text-blue-600">
                            ${product.price.toFixed(2)}
                            </p>

                            <p className="text-xs text-gray-600">
                            ⭐ {product.rating} · {product.stock} in stock
                            </p>

                            <p className="mt-1 text-xs text-blue-600">
                            View product →
                            </p>
                        </div>
                        </a>
                    ))}
                    </div>
                )}
                </>
              </div>
            ))}

            {loading && (
              <p className="text-sm text-gray-500">
                Finding products...
              </p>
            )}
          </div>

          {/* Message input */}
          <form
            className="flex gap-2 border-t p-3"
            onSubmit={(event) => {
              event.preventDefault();
              void sendMessage();
            }}
          >
            <input
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask about products..."
              className="min-w-0 flex-1 rounded-lg border px-3 py-2 text-sm text-gray-900"
            />

            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </div>
      )}

      {/* Floating chat button */}
      <button
        type="button"
        onClick={() => setIsOpen((previous) => !previous)}
        className="ml-auto block rounded-full bg-blue-600 px-5 py-4 font-semibold text-white shadow-lg"
      >
        {isOpen ? "Close" : "Ask Shop AI"}
      </button>
    </div>
  );
}
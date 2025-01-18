from fastapi import FastAPI, Request
import redis.asyncio as redis
import openai
from classifier import classify_query

app = FastAPI()
client = openai.Client(api_key="YOUR_API_KEY")
cache = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@app.post("/query")
async def handle_query(request: Request):
    data = await request.json()
    query = data.get("query")
    if not query:
        return {"error": "Query is required"}
    cached_response = await cache.get(query)
    if cached_response:
        return {"response": cached_response}
    complexity = classify_query(query)
    model = "gpt-3.5-turbo" if complexity == "simple" else "gpt-4o"
    response = await client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": query}]
    )
    response_text = response.choices[0].message.content
    await cache.set(query, response_text)
    return {"response": response_text}

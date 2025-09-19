import os 
import asyncio
from dotenv import load_dotenv , find_dotenv
from pinecone import Pinecone, ServerlessSpec
from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel 
_:bool = load_dotenv(find_dotenv()) # read local .env file
pinecone_api_key = os.getenv("PINECONE_API_KEY")
# Initialize Pinecone v3 client
pc = Pinecone(api_key=pinecone_api_key)
gemini_api_key = os.getenv("GEMINI_API_KEY")
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://api.generativeai.google/v1beta2/"
)
model = OpenAIChatCompletionsModel(
    model = "gemini-2.5-flash",
    openai_client=provider
)
# Create an index if it doesn't exist
index_name = "teaching-assistant-index"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=3072,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
index = pc.Index(index_name)

async def embed_texts(texts: list[str], model: str = "gemini-embedding-004"):
    """
    Return embeddings for texts using Gemini through OpenAI SDK.
    """
    resp = await provider.embeddings.create(
        model=model,
        input=texts
    )
    embeddings = [d.embedding for d in resp.data]
    return embeddings

async def main():
    docs = [
        {"id": "1", "text": "In Python, a variable is a name that refers to a value. You can create one using the assignment operator, e.g., x = 5."},
        {"id": "2", "text": "The capital of France is Paris. It has been France’s capital city for over 1000 years."},
        {"id": "3", "text": "Newton's Second Law states that Force equals mass times acceleration (F = m * a)."},
    ]

    # Embed and upsert documents into Pinecone
    embeddings = await embed_texts([doc["text"] for doc in docs])
    vectors = [
        {"id": d["id"], "values": emb, "metadata": {"text": d["text"]}}
        for d, emb in zip(docs, embeddings)
    ]
    index.upsert(vectors=vectors)

    # User's query
    query = "How do I create a variable in Python?"
    # Embed the query
    q_resp = await provider.embeddings.create(input=query, model="gemini-embedding-001")
    q_embedding = q_resp.data[0].embedding

    # Query Pinecone for top 2 similar vectors
    result = index.query(vector=q_embedding, top_k=2, include_metadata=True)
    for match in result["matches"]:
        score = match["score"]
        text = match["metadata"]["text"]
        print(f"Score: {score:.3f}, Retrieved text: {text[:60]}...")


if __name__ == "__main__":
    asyncio.run(main())
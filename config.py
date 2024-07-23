import os
from pinecone import Pinecone

from langchain_together import Together
from openai import OpenAI
import tiktoken
import cohere
import together


#

mistral_client = OpenAI(
    api_key="API_KEY",
    base_url="https://api.together.xyz/v1",
)


openai_client = OpenAI(
    api_key="API_KEY",
)
embedding_model_name = "text-embedding-3-small"


llm = Together(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    temperature=0.7,
    max_tokens=128,
    top_k=1,
    together_api_key="API_KEY",
)

PINECONE_API_KEY = "API_KEY"
INDEX_NAME = "INDEX_NAME"
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index(INDEX_NAME)


# Tiktoken Configuration
tokenizer_model = "cl100k_base"
tokenizer = tiktoken.get_encoding(tokenizer_model)
chunk_size = 1000
chunk_overlap = 100


# Cohere Rerank Configuration
cohere_instance = cohere.Client("API_KEY")
top_k_rerank_results = int(5)


cron_time_in_minutes = 1

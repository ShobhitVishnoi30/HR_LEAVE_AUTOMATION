from document_utils.extract_text_and_create_chunks import (
    create_embeddings_and_insert,
    extract_and_save_pdf_attachment,
    split_text_in_chunks,
)
from config import openai_client, embedding_model_name, pinecone_index, cohere_instance


def extract_data_and_insert_into_pinecone(filepath, namespace):
    text = extract_and_save_pdf_attachment(filepath)
    docs = split_text_in_chunks(text)
    pinecone_ids = create_embeddings_and_insert(
        docs, openai_client, embedding_model_name, pinecone_index, namespace
    )
    return pinecone_ids


def generate_LLM_response(query, texts, LLM):
    if texts == "":
        return "I don't know about this topic"
    # Construct the assistant's response template
    template = f"""
        Role: You are a helpful assistant specialized in providing answers when provided with the knowledge base.
        1.Your task is to provide the answer for the query using the knowledge base provided.
        2.Check the relevant information from the knowledge base.
        3.If the answer is available then create a reply for the query.
        4.Make Sure your reply is detailed and each point is covered in the reply.Do not deviate from the original query.
        5.Only stick with the query .Do not explain irrelevant and unwanted information which is not directly related to the query.
        6.Never use your knowledge to provide the answer for the query.
        7.If answer is not available in the knowledge base then simply say "I don't know about this topic"
        Query: {query}

        Knowledge base: {texts}
    """
    response = ""
    # Prepare the conversation messages
    messages = [{"role": "user", "content": template}]
    if LLM == "openai":

        res = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            temperature=0.7,
            # stream=True,
        )
        response = res.choices[0].message.content
        # for chunk in res:
        #     yield chunk.choices[0].delta.content

    return response


def get_reply_normally(query, namespace, LLM):
    # Create embeddings of the query text using the specified embedding model
    response = openai_client.embeddings.create(input=query, model=embedding_model_name)
    # Extract the query embeddings
    query_embeddings = response.data[0].embedding

    # Query the Pinecone index with the query embeddings and filter by user
    pinecone_result = pinecone_index.query(
        vector=[query_embeddings],
        top_k=20,
        include_metadata=True,
        namespace=namespace,
    )

    docs = {x["metadata"]["text"]: i for i, x in enumerate(pinecone_result["matches"])}
    rerank_docs = cohere_instance.rerank(
        query=query,
        documents=docs.keys(),
        top_n=3,
        model="rerank-english-v2.0",
    )

    sources = {"results": []}
    texts = ""
    if rerank_docs:
        for i, doc in enumerate(rerank_docs):
            if doc.relevance_score > 0.5:
                index_of_pinecone = doc.index
                if index_of_pinecone is not None and 0 <= index_of_pinecone < len(
                    pinecone_result["matches"]
                ):
                    specific_result = pinecone_result["matches"][index_of_pinecone]
                    result_dict = {
                        "text": specific_result["metadata"]["text"],
                    }
                    sources["results"].append(result_dict)
                else:
                    print(f"Index {index_of_pinecone} is out of range.")
                texts += doc.document["text"]
    data = generate_LLM_response(query, texts, LLM)
    return data

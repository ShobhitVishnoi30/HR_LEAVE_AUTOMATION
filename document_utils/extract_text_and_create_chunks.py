import pdf2image
import pytesseract
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import tokenizer, chunk_size, chunk_overlap
from uuid import uuid4


def create_embeddings_and_insert(
    docs, client, embedding_model_name, pinecone_index, namespace
):
    print("creating embeddings")
    metadata = []
    pinecone_ids = []  # List to store generated IDs

    # Use OpenAI to generate embeddings for the text chunks
    embeddings = client.embeddings.create(input=docs, model=embedding_model_name)

    for i, record in enumerate(embeddings.data):
        data = {
            "id": str(uuid4()),
            "values": record.embedding,
            "metadata": {"text": docs[i]},
        }
        metadata.append(data)
        pinecone_ids.append(data["id"])

    pinecone_index.upsert(vectors=metadata, namespace=namespace)

    return pinecone_ids


def extract_and_save_pdf_attachment(file_path):
    print("fetching data")
    try:
        text = ""
        image = pdf2image.convert_from_path(file_path)
        for pagenumber, page in enumerate(image):
            detected_text = pytesseract.image_to_string(page)
            text = text + " " + detected_text.replace("\n", " ").replace("\r", "")
        return text
    except Exception as e:
        print(e)
        return ""
        # raise e


def token_len(text):
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)


def split_text_in_chunks(text):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=token_len,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = text_splitter.split_text(text)
    return chunks

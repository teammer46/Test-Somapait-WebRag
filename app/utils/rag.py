from .chroma_client import collection
from .embedding import embed

def add_document(chunks: list):

    docs = []
    ids = [f"tilda_{i}" for i in range(len(chunks))]

    for idx, faq in enumerate(chunks):
        
        # แปลง dict → string
        text = str(
            f"Section: {faq['section']}\n"
            f"Question: {faq['question']}\n"
            f"Answer: {faq['answer']}"
        )

        docs.append(text)

    # 2) สร้าง embeddings ด้วย model
    embeddings = embed(docs)

    # 3) Add เข้า Chroma พร้อม embeddings
    collection.add(
        ids=ids,
        documents=docs,
        embeddings=embeddings
    )


def query_rag(question: str, top_k=3):

    # embed question ด้วย model
    query_embed = embed(question)

    result = collection.query(
        query_embeddings=[query_embed],
        n_results=top_k
    )
    return result

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.utils.llm import call_llm_with_tools, call_llm_with_docs
from app.utils.mongo_util import(
                                    save_history_mongo, list_histories,
                                    load_history_by_title, 
                                    del_history as delete_history, 
                                    rename_title
                                )
from app.utils.rag import add_document, query_rag
import re
from app.utils.chroma_client import collection
from app.utils.scraping import scrape_url
from app.model.schemas import (
                                ChatPayload,
                                CreateRoomPayload,
                                RenamePayload
)




@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔍 Checking Chroma DB...")

    # ดูว่ามีเอกสารหรือยัง
    count = collection.count()

    if count == 0:
        print("📭 No data found in Chroma. Auto-scraping...")
        faqs = scrape_url()
        add_document(faqs)
        print(f"📚 Indexed {len(faqs)} FAQ documents into Chroma.")
    else:
        print(f"📚 Chroma already contains {count} documents, skipping indexing.")

    yield

    print("🔻 Application shutting down...")


app = FastAPI(
    lifespan=lifespan,
    title="Company Chatbot with Gemini + RAG + MongoDB"
    )

# --------------------------
# API: Chat
# --------------------------

@app.post("/chat")
def chat_api(payload: ChatPayload):
    # Step 1) LLM ตีความว่าต้อง call function หรือไม่
    llm_result = call_llm_with_tools(payload.message, payload.title)

    # Case 1: LLM ต้องการ function_call → เรียก RAG
    print(llm_result["type"] == "function_call")
    if llm_result["type"] == "function_call":
        query = llm_result["arguments"]["query"]
        top_k = llm_result["arguments"].get("top_k", 3)

        rag_docs = query_rag(query, top_k=top_k)

        # แปลงกลับให้เหมาะกับ docs จาก Web Scraping
        docs = []
        for i in range(len(rag_docs["documents"][0])):
            section_match = re.search(r"Section:\s*(.+)", rag_docs["documents"][0][i])
            question_match = re.search(r"Question:\s*(.+)", rag_docs["documents"][0][i])
            answer_match = re.search(r"Answer:\s*([\s\S]+)", rag_docs["documents"][0][i])
            docs.append({
                "section": section_match,
                "question": question_match,  
                "answer": answer_match
            })
        final = call_llm_with_docs(payload.message, docs, llm_result["title"])

        return {
            "answer": final["answer"],
            "title": final["title"]
        }

    # Case 2: ตอบเองได้ → final
    return {
            "answer": llm_result["answer"],
            "title": llm_result["title"]
    }

# --------------------------
# API: List All History
# --------------------------

@app.get("/history/list")
def list_history_api():
    return list_histories()


# --------------------------
# API: Load history (by ID)
# --------------------------

@app.get("/history/{title}")
def load_history_api(title: str):
    messages = load_history_by_title(title)
    return {"messages": messages}


# --------------------------
# API: Create Room
# --------------------------

@app.post("/history/create")
def create_room_api(payload: CreateRoomPayload):
    save_history_mongo(payload.title, chat=None)  # สร้างห้องเปล่า
    return {"title": payload.title}


# --------------------------
# API: Delete History
# --------------------------

@app.delete("/history/{title}")
def delete_history_api(title: str):
    delete_history(title)
    return {"status": "deleted", "title": title}


# --------------------------
# API: Rename Room
# --------------------------

@app.put("/history/rename")
def rename_api(payload: RenamePayload):
    rename_title(payload.session_id, payload.new_title)
    return {"status": "renamed"}

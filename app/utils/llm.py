from google import genai
from google.genai import types
import time
from datetime import datetime
from .mongo_util import Chat
from .mongo_util import save_history_mongo, load_history_by_title

GENMINI_API_KEY = "AIzaSyCUMDvCcMm0sBkEORCL1i9WpzGI6krcYTE"

client = genai.Client(api_key=GENMINI_API_KEY)

# -----------------------
# Tools (Function Calling)
# -----------------------

retrieve_faq_docs = {
    "name": "retrieve_faq_docs",
    "description": "ตอบคำถามที่ไม่รู้คำตอบ, ค้นหาและดึงข้อมูล FAQ ที่ได้จากการ Web Scraping หรือฐานความรู้ภายในของบริษัท Tilda",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "top_k": {"type": "number"}
        },
        "required": ["query"]
    }
}

tools = types.Tool(function_declarations=[retrieve_faq_docs])
config = types.GenerateContentConfig(tools=[tools])

def build_history(title: str):
    raw = load_history_by_title(title)
    history = []

    for msg in raw:
        history.append({
            "role": msg["role"],     # "user" / "assistant"
            "message": msg["message"]
        })

    return history

def history_to_string(history_raw: list) -> str:
    if not history_raw:
        return "[]"
    print(history_raw)
    
    lines = []
    for h in history_raw:
        lines.append(f'{{"role": "{h["role"]}", "message": "{h["message"]}"}}')
    
    return "[\n" + ",\n".join(lines) + "\n]"


# -----------------------
# Utility
# -----------------------

def generate_default_title(question: str) -> str:
    if not question:
        return "chat-" + datetime.now().strftime("%Y%m%d-%H%M")

    words = question.strip().split()
    return "-".join(words[:3]).lower()


# ---------------------------------------------------
# 1) LLM → ถ้าเรียก function (RAG) → เราจะไป query docs
# ---------------------------------------------------

def call_llm_with_tools(question: str, title: str = None):
    final_title = title if title else generate_default_title(question)

    history = build_history(final_title)
    history_str = history_to_string(history)

    messages = f"นี่คือประวัติการสนทนาที่ผ่านมา โปรดอ่านก่อนตอบ:\n{history_str}" + "If you don't know the answer, lack sufficient information, or the question requires external/updated/structured data, you MUST call the tool `retrieve_faq_docs`." + question

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=messages,
        config=config
    )

    msg = response.candidates[0].content

    # ถ้า LLM เรียก Function
    if msg.parts and getattr(msg.parts[0], "function_call", None):
        fn = msg.parts[0].function_call

        return {
            "title": final_title,
            "type": "function_call",
            "function_name": fn.name,
            "arguments": fn.args
        }

    # ถ้า LLM ตอบเอง → บันทึกและส่งกลับ
    answer = response.text

    save_history_mongo(final_title, Chat(role="user", message=question))
    save_history_mongo(final_title, Chat(role="assistant", message=answer))

    return {
        "title": final_title,
        "type": "final",
        "answer": answer
    }


# ---------------------------------------------------
# 2) LLM → ตอบด้วย Context จาก Web Scraping (Docs)
# ---------------------------------------------------

def call_llm_with_docs(question: str, docs: list, title: str = None):

    history = build_history(title)
    history_str = history_to_string(history)

    
    # แปลงเป็น context ที่มีความหมาย
    context_blocks = [
        f"[หมวด: {d['section']}]\nQ: {d['question']}\nA: {d['answer']}"
        for d in docs
    ]

    context = "\n\n".join(context_blocks)

    # Prompt (เวอร์ชันปรับปรุงสำหรับข้อมูลบริษัท)
    prompt = f"""
คุณคือผู้ช่วยตอบคำถามเกี่ยวกับบริษัท โดยใช้ข้อมูลจาก FAQ ด้านล่างนี้เท่านั้น

======================
ข้อมูลที่ใช้ได้:
{context}
======================

คำถาม:
{question}

วิธีตอบ:
1. ตอบสั้น กระชับ ชัดเจน เหมือนการใช้ RAG
2. อ้างอิงเฉพาะข้อมูลจาก FAQ เท่านั้น
3. ถ้าไม่มีข้อมูล ให้ตอบว่า "จากฐานข้อมูล ไม่พบคำตอบสำหรับคำถามนี้"
"""
    messages = f"นี่คือประวัติการสนทนาที่ผ่านมา โปรดอ่านก่อนตอบ:\n{history_str}" + prompt

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=messages
    )

    final_title = title if title else generate_default_title(question)

    save_history_mongo(final_title, Chat(role="user", message=question))
    save_history_mongo(final_title, Chat(role="assistant", message=response.text))

    return {
        "answer": response.text,
        "title": final_title
    }

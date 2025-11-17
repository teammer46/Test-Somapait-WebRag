ด้านล่างนี้คือ **README.md แบบสวย-เป็นระเบียบ** สำหรับโปรเจกต์ที่มี **FastAPI + Streamlit** พร้อมคำอธิบายวิธีรันทุกส่วน
— เอาไปวางใน GitHub ได้เลย 👍

---

# 🚀 FastAPI + Streamlit Project

ระบบนี้เป็นเว็บแอปที่ประกอบด้วย

* **FastAPI** สำหรับ Backend API
* **Streamlit** สำหรับ Frontend UI
* รองรับการอัปโหลดไฟล์, RAG, AI chatbot หรือ API อื่น ๆ ที่คุณสร้างเพิ่มเติม

---

## 📦 1. Requirements

ให้ติดตั้ง Python version: **Python 3.10+**

จากนั้นรัน:

```bash
pip install -r requirements.txt
```

✨ *ตัวอย่างไฟล์ requirements.txt*

```
fastapi
uvicorn
pydantic
python-multipart
streamlit
requests
```

---

## 📁 2. โครงสร้างโปรเจกต์ (แนะนำ)

```
project/
│
├── app/
│   ├── main.py            # FastAPI backend
│   ├── routers/           # (optional) API แยกเป็น module
│   ├── utils/             # helper functions
│   └── models/            # pydantic models
│
├── streamlit_app/
│   └── app.py             # Streamlit UI
│
├── requirements.txt
└── README.md
```

---

# 🔥 3. วิธีรัน FastAPI

เข้าโฟลเดอร์หลัก แล้วรัน:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

เปิดดู Document ได้ที่:

👉 **[http://localhost:8000/docs](http://localhost:8000/docs)** (Swagger UI)
👉 **[http://localhost:8000/redoc](http://localhost:8000/redoc)**

---

### ตัวอย่าง `app/main.py`

```python
from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}
```

---

# 🖥️ 4. วิธีรัน Streamlit

รัน UI ด้วยคำสั่ง:

```bash
streamlit run streamlit_app/app.py
```

Streamlit จะรันที่:

👉 **[http://localhost:8501](http://localhost:8501)**

---

### ตัวอย่าง `streamlit_app/app.py`

```python
import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("📤 File Upload (FastAPI + Streamlit)")

uploaded = st.file_uploader("Upload file", type=["png","jpg","jpeg","pdf"])

if uploaded is not None:
    files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
    res = requests.post(f"{API_URL}/upload", files=files)

    if res.status_code == 200:
        st.json(res.json())
    else:
        st.error(f"Upload failed: {res.status_code} - {res.text}")
```

---

# 🧪 5. ทดสอบระบบ

### 1) ทดสอบ API

เปิด:

```
http://localhost:8000/docs
```

ลองยิง `/upload`

### 2) ทดสอบ Streamlit

อัปโหลดไฟล์และเชื่อมกับ API ฝั่ง FastAPI

---

# 🧩 6. ใช้ FastAPI + Streamlit พร้อมกัน

เปิด 2 terminal:

### Terminal 1 – FastAPI

```bash
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 – Streamlit

```bash
streamlit run streamlit_app/app.py
```

---

# 🛡️ 7. ปัญหาที่พบบ่อย

### ❗ Streamlit เรียก API แล้ว Error `CORS`

เพิ่มใน FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

# 📌 8. Deploy (Optional)

คุณสามารถ deploy ได้หลายรูปแบบ เช่น

* **FastAPI** ลงบน Uvicorn/Gunicorn + Docker
* **Streamlit Cloud**
* **Render**
* **Railway**
* **AWS/EC2 / Google Cloud Run / Azure**

---

# 🎉 เสร็จเรียบร้อย!

ถ้าต้องการ **README แบบโปรระดับบริษัท**, หรืออยากใส่ **รูป Diagram**, **API examples**, **ภาพโปรเจกต์**, บอกได้เลย เดี๋ยวจัดให้!

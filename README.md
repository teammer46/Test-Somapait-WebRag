ด้านล่างนี้คือ **README.md แบบสวย-เป็นระเบียบ** สำหรับโปรเจกต์ที่มี **FastAPI + Streamlit** พร้อมคำอธิบายวิธีรันทุกส่วน
— เอาไปวางใน GitHub ได้เลย 👍

---

# 🚀 FastAPI + Streamlit Project

ระบบนี้เป็นเว็บแอปที่ประกอบด้วย

* **FastAPI** สำหรับ Backend API
* **Streamlit** สำหรับ Frontend UI

---

## 📦 1. Requirements

ให้ติดตั้ง Python version: **Python 3.10+**

จากนั้นรัน:

```bash
pip install -r requirements.txt
```

# 🔥 2. วิธีรัน FastAPI

เข้าโฟลเดอร์หลัก แล้วรัน:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

เปิดดู Document ได้ที่:

👉 **[http://localhost:8000/docs](http://localhost:8000/docs)** (Swagger UI)
👉 **[http://localhost:8000/redoc](http://localhost:8000/redoc)**


# 🖥️ 3. วิธีรัน Streamlit

รัน UI ด้วยคำสั่ง:

```bash
streamlit run streamlit_app/app.py
```

Streamlit จะรันที่:

👉 **[http://localhost:8501](http://localhost:8501)**



# 🧩 4. ใช้ FastAPI + Streamlit พร้อมกัน

เปิด 2 terminal:

### Terminal 1 – FastAPI

```bash
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 – Streamlit

```bash
streamlit run streamlit_app/app.py
```



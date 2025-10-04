# supabase_dockerfile/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# คัดลอก requirements.txt จาก root
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดจากโฟลเดอร์ app เข้า container
COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7001"]

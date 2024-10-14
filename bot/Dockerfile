FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -U -r requirements.txt

COPY . .

CMD ["python", "-m", "main"]

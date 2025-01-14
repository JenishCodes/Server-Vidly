FROM python:3.13.0-slim

WORKDIR /vidly

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", ":5000", "main:app"]

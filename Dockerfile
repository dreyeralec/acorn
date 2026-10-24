FROM python:3.13.5-slim

WORKDIR /acorn

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "acorn"]
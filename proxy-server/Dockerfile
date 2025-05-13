FROM python:3.13

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["mitmdump", "--mode", "regular", "-s", "server.py", "--listen-port", "8080"]

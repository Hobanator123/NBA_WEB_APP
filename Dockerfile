FROM python:3.10-slim

WORKDIR /code

COPY ./src/requirements.txt ./src/requirements.txt

RUN pip install --no-cache-dir -r src/requirements.txt

COPY ./src ./src

CMD ["python" , "./src/main.py"]

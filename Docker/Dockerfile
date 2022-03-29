FROM python:3.9-buster

COPY . /app

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

#CMD ["uvicorn", "API.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
ENTRYPOINT ["./entrypoint.sh"]

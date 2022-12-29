FROM python:3.9-bullseye

ENV PIP_NO_CACHE_DIR=1

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.docker.txt
RUN pip install -e .

RUN chmod +x Docker/entrypoint.sh

#CMD ["uvicorn", "API.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
ENTRYPOINT ["Docker/entrypoint.sh"]

HEALTHCHECK CMD curl -f http://localhost:8000 || exit 1

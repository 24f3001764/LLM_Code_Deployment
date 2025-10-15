# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

# Declare build-time variables
ARG MODEL_REPO_NAME
ENV MODEL_NAME=$MODEL_REPO_NAME

# Use in your application
RUN echo "Using model: $MODEL_NAME"

FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*
COPY nginx.conf /etc/nginx/nginx.conf

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
 && rm -rf /var/lib/apt/lists/*


FROM python:3.9

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user . /app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]

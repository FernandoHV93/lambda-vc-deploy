FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

# System deps (add libsndfile for soundfile if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Python deps; pin as appropriate for your models
RUN pip install --no-cache-dir runpod boto3 soundfile pydantic

# Copy project
COPY . /workspace

# Default envs (override in Runpod console)
ENV LAMBDA_VC_BUCKET_NAME="" \
    LAMBDA_VC_WEBHOOK_SECRET=""

# Entry: Runpod Serverless handler
CMD ["python3", "-u", "rp_handler.py"]



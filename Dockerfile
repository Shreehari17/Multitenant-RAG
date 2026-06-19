FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

# Install CPU-only PyTorch (updated to 2.5.1 for compatibility)
RUN pip install --no-cache-dir \
    torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu

# Install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
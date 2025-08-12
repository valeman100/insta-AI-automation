FROM python:3.11.4-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1

# Default command can be overridden at runtime
CMD ["python", "main/main_ai.py"]
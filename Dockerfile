FROM python:3.13-slim

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY . .

RUN uv pip install --system --no-cache --group dev .

EXPOSE 8000

CMD ["scvi-tools-mcp"]

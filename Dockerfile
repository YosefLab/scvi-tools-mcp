FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY . .

RUN uv pip install --system --no-cache ".[dev]"

EXPOSE 8000

CMD ["scvi-tools-mcp"]

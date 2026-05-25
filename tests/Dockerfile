FROM python:3.14-slim
WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "pytest", "-v", "--tb=short"]

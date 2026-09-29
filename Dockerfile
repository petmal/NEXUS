FROM python:3.14.7-slim-trixie@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d

WORKDIR /app

ENV UV_NO_CACHE=1
ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN python -m pip install --no-cache-dir --no-deps uv==0.12.19 \
    && uv sync --frozen --extra server --no-editable

ENTRYPOINT ["nexus"]

FROM python:3.14.7-slim-trixie@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d

ARG VCS_REF=unknown
LABEL org.opencontainers.image.revision="${VCS_REF}"

WORKDIR /app

ENV UV_NO_CACHE=1
ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY scripts/prepare_package.py scripts/preflight_repair.py scripts/preflight_matrix.py ./scripts/
COPY docs/difficulty-model-matrix.json ./docs/difficulty-model-matrix.json

RUN python scripts/prepare_package.py \
    && python -m pip install --no-cache-dir --no-deps uv==0.12.21 \
    && uv sync --frozen --extra server --no-editable \
    && python -c "from nexus.ontology.repair.qualification import require_release; require_release()"

ENTRYPOINT ["nexus"]

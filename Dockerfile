FROM python:3.8.10-slim as base

ARG VERSION

# TODO: limitation imposed by osparc!
ENV SC_USER_ID 8004
ENV SC_USER_NAME app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN addgroup --gid ${SC_USER_ID} --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid ${SC_USER_ID} --system --group app


FROM base as builder


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm --recursive --force /var/lib/apt/lists/*


WORKDIR /build

COPY --chown=app:app README.md pyproject.toml /build/
COPY --chown=app:app src  /build/src


RUN pip --no-cache-dir install --upgrade \
    pip \
    setuptools \
    wheel \
    && pip --no-cache-dir wheel --wheel-dir=/build/wheels /build/


FROM base as production

COPY --from=builder --chown=app:app /build/wheels /wheels

RUN pip --no-cache-dir install --upgrade pip \
    && pip --no-cache-dir install /wheels/* \
    && rm -rf /wheels

USER app
WORKDIR /app
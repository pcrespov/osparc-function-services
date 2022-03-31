FROM python:3.8.10-slim as base

RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm --recursive --force /var/lib/apt/lists/*


WORKDIR /build

COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} . .

RUN pip --no-cache install --upgrade \
    pip \
    setuptools \
    wheel \
    && pip --no-cache install --use-feature=in-tree-build  .

#&& pip --no-cache install "git+https://github.com/ITISFoundation/osparc-simcore.git@master#egg=simcore-models-library&subdirectory=packages/models-library" \
#&& pip --no-cache install "git+https://github.com/ITISFoundation/osparc-simcore.git@master#egg=simcore-service-integration&subdirectory=packages/service-integration"


USER app
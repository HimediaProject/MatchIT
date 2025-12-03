FROM postgres:18

# Install build dependencies and build pgvector from source
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        git \
        llvm \
        libssl-dev \
        postgresql-server-dev-18 \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && cd /tmp/pgvector \
    && make \
    && make install \
    && rm -rf /tmp/pgvector \
    && apt-get purge -y --auto-remove git build-essential ca-certificates libssl-dev postgresql-server-dev-18 \
    && rm -rf /var/lib/apt/lists/*

USER postgres

EXPOSE 5432

CMD ["postgres"]

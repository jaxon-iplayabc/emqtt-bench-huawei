ARG FROM=ghcr.io/emqx/emqx-builder/5.5-2:1.18.3-27.2-3-debian12
ARG PLATFORM=linux/amd64
FROM --platform=${PLATFORM} ${FROM} AS builder
COPY . /emqtt_bench
WORKDIR /emqtt_bench
ENV BUILD_WITHOUT_QUIC=1
RUN make release

#FROM debian:12-slim
FROM --platform=${PLATFORM} ghcr.io/astral-sh/uv:debian

COPY --from=builder /emqtt_bench/emqtt-bench-*.tar.gz /emqtt_bench/

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates procps curl; \
    rm -rf /var/lib/apt/lists/*; \
    groupadd -r -g 1000 emqtt_bench; \
    useradd -r -m -u 1000 -g emqtt_bench emqtt_bench; \
    cd /emqtt_bench && \
    tar zxf emqtt-bench-*.tar.gz && \
    rm emqtt-bench-*.tar.gz && \
    chown -R emqtt_bench:emqtt_bench /emqtt_bench
RUN ls /emqtt_bench/
RUN mv /emqtt_bench/erts-15.2* /emqtt_bench/erts-15.2.7.2
#ENTRYPOINT ["/emqtt_bench/bin/emqtt_bench"]
#CMD [""]




#FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:debian
#COPY --from=builder /emqtt_bench /emqtt_bench
ENV PATH=/emqtt_bench/bin:$PATH
RUN mkdir -p /app
WORKDIR /app
COPY ./metrics /app
RUN uv venv && uv sync

RUN find . -type f -name "*.pyc" -delete && \
    find . -type d -name "__pycache__" -delete

#ENTRYPOINT ["cd /app && uv run main.py"]
#CMD [""]
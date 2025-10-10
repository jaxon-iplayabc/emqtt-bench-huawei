#ARG FROM=ghcr.io/emqx/emqx-builder/5.5-2:1.18.3-27.2-3-debian12
ARG PLATFORM=linux/amd64

###### build a mqtt-stress-tool-builder
#FROM --platform=${PLATFORM} ${FROM} AS builder
#
## 使用缓存卷来持久化构建产物
#VOLUME /build-cache
#
#COPY . /emqtt_bench
#WORKDIR /emqtt_bench
#ENV BUILD_WITHOUT_QUIC=1
#RUN make release
## will created _build/emqtt_bench/rel/emqtt_bench/emqtt_bench-0.0.0.tar.gz
#
##FROM debian:12-slim
##FROM --platform=${PLATFORM} ghcr.io/astral-sh/uv:debian
#FROM debian:12-slim # use this
#COPY --from=builder /emqtt_bench/emqtt-bench-*.tar.gz /emqtt_bench/
#
#RUN set -eux; \
#    apt-get update; \
#    apt-get install -y --no-install-recommends ca-certificates procps curl; \
#    rm -rf /var/lib/apt/lists/*; \
#    groupadd -r -g 1000 emqtt_bench; \
#    useradd -r -m -u 1000 -g emqtt_bench emqtt_bench; \
#    cd /emqtt_bench && \
#    tar zxf emqtt-bench-*.tar.gz && \
#    rm emqtt-bench-*.tar.gz && \
#    chown -R emqtt_bench:emqtt_bench /emqtt_bench
#RUN ls /emqtt_bench/
#RUN mv /emqtt_bench/erts-15.2* /emqtt_bench/erts-15.2.7.2
##ENTRYPOINT ["/emqtt_bench/bin/emqtt_bench"]
##CMD [""]
######## finish mqtt-stress-tool-builder



FROM --platform=${PLATFORM}  mqtt-stress-tool-builder:1 AS builder2
FROM --platform=${PLATFORM} ghcr.io/astral-sh/uv:debian
COPY --from=builder2 /emqtt_bench /emqtt_bench
ENV PATH=/emqtt_bench/bin:$PATH
RUN mkdir -p /app2
WORKDIR /app2
COPY ./metrics /app2

RUN find . -type f -name "*.pyc" -delete && \
    find . -type d -name "__pycache__" -delete
RUN echo '=====================list /app========================'
RUN ls -R
RUN echo '====================do uv========================='
RUN uv venv && uv sync
RUN echo '====================list /app after uv========================='
RUN ls -R

RUN chmod +x /app2/run.sh
ENTRYPOINT ["/app2/run.sh"]
CMD ["bash"]
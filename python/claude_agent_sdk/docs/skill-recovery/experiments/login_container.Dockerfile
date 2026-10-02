ARG BASE_IMAGE
FROM ${BASE_IMAGE}
COPY runtime /opt/python
COPY packages /opt/packages
COPY claude /opt/claude
RUN mkdir -p /home/proof/.claude /work && chown -R 1000:1000 /home/proof /work
ENV HOME=/home/proof
ENV CLAUDE_CONFIG_DIR=/home/proof/.claude
ENV PYTHONPATH=/opt/packages
ENV DISABLE_AUTOUPDATER=1
USER 1000:1000
WORKDIR /work
ENTRYPOINT ["/opt/claude"]

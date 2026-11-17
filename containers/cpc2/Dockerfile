# CPC2 1.0.1 standalone (Bioconda build, executed unmodified; model is bundled with the tool).
FROM quay.io/biocontainers/cpc2:1.0.1--hdfd78af_1@sha256:eafa23ee6ca2c974a6ec6e0591b2dca8ac7f12846facda9581e69d57124cd0f0
LABEL org.opencontainers.image.title="CPC2" \
      org.opencontainers.image.version="1.0.1" \
      org.opencontainers.image.source="https://github.com/gao-lab/CPC2_standalone" \
      org.opencontainers.image.licenses="GPL-3.0" \
      metalncrna.base="quay.io/biocontainers/cpc2:1.0.1--hdfd78af_1@sha256:eafa23ee6ca2c974a6ec6e0591b2dca8ac7f12846facda9581e69d57124cd0f0" \
      metalncrna.modified="false"
COPY run-cpc2 /usr/local/bin/run-cpc2
ENTRYPOINT ["run-cpc2"]

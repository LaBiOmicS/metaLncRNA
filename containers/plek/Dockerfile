# PLEK 1.2 (Bioconda build, executed unmodified; model is bundled with the tool).
# The py310 build is used because the py312 build fails: PLEK.py opens files with mode 'rU',
# which Python 3.11 removed.
FROM quay.io/biocontainers/plek:1.2--py310h8ea774a_10@sha256:6d7ccf0392b0d7efa2a2d893d08a88410b4b138a7b1ce21fd487c690c574e45c
LABEL org.opencontainers.image.title="PLEK" \
      org.opencontainers.image.version="1.2" \
      org.opencontainers.image.source="https://sourceforge.net/projects/plek/" \
      org.opencontainers.image.licenses="GPL-2.0" \
      metalncrna.base="quay.io/biocontainers/plek:1.2--py310h8ea774a_10@sha256:6d7ccf0392b0d7efa2a2d893d08a88410b4b138a7b1ce21fd487c690c574e45c" \
      metalncrna.modified="false"
COPY run-plek /usr/local/bin/run-plek
ENTRYPOINT ["run-plek"]

# CNCI v2 (www-bioinfo-org/CNCI @ 745e2d1), executed UNMODIFIED.
# Only build-time action on upstream: compile the bundled libsvm-3.0, as the CNCI README instructs.
FROM debian:bookworm-slim@sha256:734a72b3d6142a71993b4bc580ca01d8ca687f77a2c422d96a961d3376b179bc AS build
RUN apt-get update && apt-get install -y --no-install-recommends g++ make unzip && rm -rf /var/lib/apt/lists/*
COPY upstream/CNCI-745e2d1942f0fa6c061f5308fdc876de430a114f.tar.gz /src/cnci.tar.gz
RUN echo "5a0a6bb0ab2847e4b4b1159ab44c76806bc4816b08456a7dbc4ab3ad78289326  /src/cnci.tar.gz" | sha256sum -c - \
 && mkdir /opt/CNCI && tar xzf /src/cnci.tar.gz -C /opt/CNCI --strip-components=1 \
 && cd /opt/CNCI && unzip -q libsvm-3.0.zip && cd libsvm-3.0 \
 # static link so the binaries run on the older glibc of the Python 2.7 runtime image
 && make CXX="g++ -static"

FROM python:2.7.18-slim-buster@sha256:6c1ffdff499e29ea663e6e67c9b6b9a3b401d554d2c9f061f9a45344e3992363
LABEL org.opencontainers.image.title="CNCI" \
      org.opencontainers.image.version="2 (745e2d1942f0fa6c061f5308fdc876de430a114f)" \
      org.opencontainers.image.source="https://github.com/www-bioinfo-org/CNCI" \
      org.opencontainers.image.licenses="GPL-2.0" \
      metalncrna.upstream.sha256="5a0a6bb0ab2847e4b4b1159ab44c76806bc4816b08456a7dbc4ab3ad78289326" \
      metalncrna.modified="false"
COPY --from=build /opt/CNCI /opt/CNCI
RUN chmod -R a+rX /opt/CNCI
COPY run-cnci /usr/local/bin/run-cnci
ENTRYPOINT ["run-cnci"]

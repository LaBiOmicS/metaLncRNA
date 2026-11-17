# LGC (ngdc.cncb.ac.cn/lgc, file "LGC-1.0.tar.gz" which is actually a RAR v4 archive holding lgc.py),
# executed UNMODIFIED.
FROM debian:bookworm-slim@sha256:734a72b3d6142a71993b4bc580ca01d8ca687f77a2c422d96a961d3376b179bc AS build
RUN apt-get update && apt-get install -y --no-install-recommends libarchive-tools && rm -rf /var/lib/apt/lists/*
COPY upstream/LGC-1.0.rar /src/LGC-1.0.rar
RUN echo "67cdbcbc6cbaabe17c71639f43c8277aad0be3466b6a6dfdb5865ddc9c55f9b6  /src/LGC-1.0.rar" | sha256sum -c - \
 && mkdir /opt/LGC && bsdtar xf /src/LGC-1.0.rar -C /opt/LGC

FROM python:2.7.18-slim-buster@sha256:6c1ffdff499e29ea663e6e67c9b6b9a3b401d554d2c9f061f9a45344e3992363
LABEL org.opencontainers.image.title="LGC" \
      org.opencontainers.image.version="1.0 download (script header: version 2.0 April 2018)" \
      org.opencontainers.image.source="https://ngdc.cncb.ac.cn/lgc/" \
      metalncrna.upstream.sha256="67cdbcbc6cbaabe17c71639f43c8277aad0be3466b6a6dfdb5865ddc9c55f9b6" \
      metalncrna.modified="false"
COPY --from=build /opt/LGC /opt/LGC
RUN chmod -R a+rX /opt/LGC
COPY run-lgc /usr/local/bin/run-lgc
ENTRYPOINT ["run-lgc"]

# RNAsamba 0.2.5 (Bioconda build, executed unmodified) + the authors' pretrained weights from the 0.2.5 tag.
FROM quay.io/biocontainers/rnasamba:0.2.5--py37h8902056_1@sha256:4b46eb4487718024405060e5e72655d68fe7308c5a90fcc5b2b9a0f27d604cfd
ADD --checksum=sha256:52e780fc44e2fcf227c7892b0c970bd22592150ab7d20e4a12e01efb8327227a https://github.com/apcamargo/RNAsamba/raw/0.2.5/data/full_length_weights.hdf5 /opt/rnasamba/full_length_weights.hdf5
ADD --checksum=sha256:befd6c2d71c9df9fe84c0c89973c462a27b4cb8a9745b031c27e6fb385f9e975 https://github.com/apcamargo/RNAsamba/raw/0.2.5/data/partial_length_weights.hdf5 /opt/rnasamba/partial_length_weights.hdf5
RUN chmod -R a+rX /opt/rnasamba
LABEL org.opencontainers.image.title="RNAsamba" \
      org.opencontainers.image.version="0.2.5" \
      org.opencontainers.image.source="https://github.com/apcamargo/RNAsamba" \
      org.opencontainers.image.licenses="GPL-3.0" \
      metalncrna.base="quay.io/biocontainers/rnasamba:0.2.5--py37h8902056_1@sha256:4b46eb4487718024405060e5e72655d68fe7308c5a90fcc5b2b9a0f27d604cfd" \
      metalncrna.modified="false"
ENV HDF5_USE_FILE_LOCKING=FALSE TF_CPP_MIN_LOG_LEVEL=2
COPY run-rnasamba /usr/local/bin/run-rnasamba
ENTRYPOINT ["run-rnasamba"]

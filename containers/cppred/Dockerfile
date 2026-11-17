# CPPred (rnabinding.com/CPPred, CPPred.tar.gz of 2018-05-17), executed UNMODIFIED.
# Uses the libsvm-3.22 binaries shipped inside the upstream tarball.
# Dependency pinned per the authors' instructions: "pip install biopython==1.75" (needs a compiler -> wheel stage)
FROM python:2.7.18-buster@sha256:d8fac68ebdc45b8d66d53f1ed6c1532da81109a8f5532a6ca0c951ed31107d70 AS wheels
RUN pip wheel --no-cache-dir -w /wheels numpy==1.16.6 biopython==1.75

FROM python:2.7.18-slim-buster@sha256:6c1ffdff499e29ea663e6e67c9b6b9a3b401d554d2c9f061f9a45344e3992363
COPY --from=wheels /wheels /wheels
RUN pip install --no-cache-dir --no-index /wheels/*.whl && rm -rf /wheels
COPY upstream/CPPred.tar.gz /tmp/CPPred.tar.gz
RUN echo "43a4eff80f5eeaa1f8266a51e38e3d288034cc36294e1d622faa1b3cb7ef4f06  /tmp/CPPred.tar.gz" | sha256sum -c - \
 && tar xzf /tmp/CPPred.tar.gz -C /opt && rm /tmp/CPPred.tar.gz && chmod -R a+rX /opt/CPPred
LABEL org.opencontainers.image.title="CPPred" \
      org.opencontainers.image.version="2018-05-17 tarball" \
      org.opencontainers.image.source="http://www.rnabinding.com/CPPred/" \
      metalncrna.upstream.sha256="43a4eff80f5eeaa1f8266a51e38e3d288034cc36294e1d622faa1b3cb7ef4f06" \
      metalncrna.modified="false"
COPY run-cppred /usr/local/bin/run-cppred
ENTRYPOINT ["run-cppred"]

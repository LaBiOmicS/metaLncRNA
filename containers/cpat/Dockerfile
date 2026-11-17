# CPAT 3.0.5 (Bioconda build, executed unmodified) + the authors' prebuilt models from the v3.0.5 tag.
FROM quay.io/biocontainers/cpat:3.0.5--py312hc9302aa_4@sha256:87366fff67d441f64e0ac4681ccbaf1147f2c0601f3df86bb99f228d7f9a9000
ADD --checksum=sha256:0266569c911d4e480896e48188875c7bbc4f8831547a7196ebcba21ec3114b29 https://raw.githubusercontent.com/liguowang/cpat/v3.0.5/prebuilt_models/Human_logitModel.RData /opt/cpat/models/Human_logitModel.RData
ADD --checksum=sha256:e1f6f715d26804ba1ada63c55803a60129ca81d485c04ff97b6caf96600cc104 https://raw.githubusercontent.com/liguowang/cpat/v3.0.5/prebuilt_models/Human_Hexamer.tsv /opt/cpat/models/Human_Hexamer.tsv
ADD --checksum=sha256:93a3473448d5cabfbfe4c4e0df6df5c222cf6c80c4bbed46b8c9954390ea3040 https://raw.githubusercontent.com/liguowang/cpat/v3.0.5/prebuilt_models/Mouse_logitModel.RData /opt/cpat/models/Mouse_logitModel.RData
ADD --checksum=sha256:a38aad27c2a9f1aa453fd86d8a15654c876543e16288c0568bb79a170d8f8502 https://raw.githubusercontent.com/liguowang/cpat/v3.0.5/prebuilt_models/Mouse_Hexamer.tsv /opt/cpat/models/Mouse_Hexamer.tsv
ADD --checksum=sha256:c595b3c8f360b11e10935cc7b55068c4aa7d05cc641dff35751b0f978500a6f8 https://raw.githubusercontent.com/liguowang/cpat/v3.0.5/prebuilt_models/Fly_logitModel.RData /opt/cpat/models/Fly_logitModel.RData
ADD --checksum=sha256:5e33b7581b03b9fffe78d43cffaf4b2c4a105ee340047da01d51030f86f57a5a https://raw.githubusercontent.com/liguowang/cpat/v3.0.5/prebuilt_models/fly_Hexamer.tsv /opt/cpat/models/Fly_Hexamer.tsv
ADD --checksum=sha256:2eb88c754f81d0d4887c8f1ac0201706ff25ce294a332b5d65a54c6522fb8089 https://raw.githubusercontent.com/liguowang/cpat/v3.0.5/prebuilt_models/Zebrafish_logitModel.RData /opt/cpat/models/Zebrafish_logitModel.RData
ADD --checksum=sha256:04e63713f7fb362ae6c019c10a712c98d46c4481f31ec65838eee11bf22e8029 https://raw.githubusercontent.com/liguowang/cpat/v3.0.5/prebuilt_models/zebrafish_Hexamer.tsv /opt/cpat/models/Zebrafish_Hexamer.tsv
RUN chmod -R a+rX /opt/cpat
LABEL org.opencontainers.image.title="CPAT" \
      org.opencontainers.image.version="3.0.5" \
      org.opencontainers.image.source="https://github.com/liguowang/cpat" \
      org.opencontainers.image.licenses="GPL-2.0-or-later" \
      metalncrna.base="quay.io/biocontainers/cpat:3.0.5--py312hc9302aa_4@sha256:87366fff67d441f64e0ac4681ccbaf1147f2c0601f3df86bb99f228d7f9a9000" \
      metalncrna.modified="false"
COPY run-cpat /usr/local/bin/run-cpat
ENTRYPOINT ["run-cpat"]

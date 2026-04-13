# Use Mambaforge as base for efficiency
FROM condaforge/mambaforge:latest

LABEL maintainer="metaLncRNA Team <fabianomenegidio@umc.br>"
LABEL version="1.1.4"
LABEL description="Docker image for metaLncRNA: A modular meta-predictor for lncRNA identification."

# Set workdir
WORKDIR /app

# Copy project files
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsvm-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install metaLncRNA and its core environment
RUN pip install --no-cache-dir .

# Run automated setup to bake all tool environments and models into the image
# This makes the image larger but ensures offline usability and instant start
RUN metalncrna setup

# Set entrypoint to the CLI
ENTRYPOINT ["metalncrna"]
CMD ["--help"]

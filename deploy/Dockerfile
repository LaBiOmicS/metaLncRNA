# Use Mambaforge as base for efficiency
FROM condaforge/mambaforge:latest

LABEL maintainer="metaLncRNA Team <fabianomenegidio@umc.br>"
LABEL version="1.2.0"
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

# Update base environment using the environment.yml
RUN mamba env update -n base -f environment.yml

# Install metaLncRNA
RUN pip install --no-cache-dir .

# Run automated setup to bake all tool environments and models into the image
RUN metalncrna setup

# Set entrypoint to the CLI
ENTRYPOINT ["metalncrna"]
CMD ["--help"]

# Base image
FROM intel/oneapi-basekit:2024.0.1-devel-ubuntu22.04

# Non-interactive setup
ARG DEBIAN_FRONTEND=noninteractive
USER root

ENV PYTHONUNBUFFERED=1

# When cache is enabled SYCL runtime will try to cache and reuse JIT-compiled binaries. 
ENV SYCL_CACHE_PERSISTENT=1

# Disable pip's cache behavior
ARG PIP_NO_CACHE_DIR=false

# Install essential tools and libraries without signature verification
RUN apt update -y --allow-insecure-repositories && \
    apt install -y --no-install-recommends --allow-unauthenticated \
    software-properties-common build-essential wget gpg curl pciutils git cmake libtbb12

# Add deadsnakes PPA and install Python 3.11
RUN add-apt-repository ppa:deadsnakes/ppa -y && apt update -y --allow-insecure-repositories && \
    apt install -y --allow-unauthenticated python3.11 python3.11-dev python3.11-distutils && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as the default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --set python3 /usr/bin/python3.11

# Install pip using get-pip.py
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 && \
    pip install --upgrade pip

RUN pip install tabulate fire

# Intel GPU Drivers
RUN wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --dearmor | tee /usr/share/keyrings/intel-oneapi-archive-keyring.gpg > /dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/intel-oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main " | tee /etc/apt/sources.list.d/oneAPI.list && \
    chmod 644 /usr/share/keyrings/intel-oneapi-archive-keyring.gpg && \
    rm /etc/apt/sources.list.d/intel-graphics.list && \
    wget -O- https://repositories.intel.com/graphics/intel-graphics.key | gpg --dearmor | tee /usr/share/keyrings/intel-graphics.gpg > /dev/null && \
    echo "deb [arch=amd64,i386 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/graphics/ubuntu jammy arc" | tee /etc/apt/sources.list.d/intel.gpu.jammy.list && \
    chmod 644 /usr/share/keyrings/intel-graphics.gpg && \
    apt update 

# Intel NPU Drivers

# OpenVINO GenAI
RUN pip install -U --pre openvino-genai openvino openvino-tokenizers[transformers] \
         --extra-index-url https://storage.openvinotoolkit.org/simple/wheels/nightly
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu \
        "git+https://github.com/huggingface/optimum-intel.git" \
        "git+https://github.com/openvinotoolkit/nncf.git" "onnx<=1.16.1"

# IPEX
RUN pip install --upgrade requests argparse urllib3 && \
    pip install --pre --upgrade ipex-llm[cpp] && \
    # Fix Trivy CVE Issues
    pip install transformers==4.36.2 && \
    pip install transformers_stream_generator einops tiktoken

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip install ollama

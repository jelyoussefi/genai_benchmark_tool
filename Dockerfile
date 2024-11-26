# Base image
FROM intel/oneapi

# Non-interactive setup
ARG DEBIAN_FRONTEND=noninteractive
USER root

# Install essential tools and libraries
RUN apt update -y && apt install -y --no-install-recommends \
    software-properties-common build-essential wget gpg curl pciutils git cmake libtbb12

# Add deadsnakes PPA and install Python 3.11
RUN add-apt-repository ppa:deadsnakes/ppa -y && apt update -y && \
    apt install -y python3.11 python3.11-dev python3.11-distutils && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as the default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --set python3 /usr/bin/python3.11

RUN apt update -y

# Install pip using get-pip.py
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 && \
    pip install --upgrade pip 

RUN pip install tabulate fire

# Intel GPU Drivers
RUN wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --dearmor | tee /usr/share/keyrings/intel-oneapi-archive-keyring.gpg > /dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/intel-oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main " | tee /etc/apt/sources.list.d/oneAPI.list && \
    chmod 644 /usr/share/keyrings/intel-oneapi-archive-keyring.gpg && \
    rm /etc/apt/sources.list.d/intel-graphics.list 

RUN apt update -y
RUN apt install -y libze1 intel-level-zero-gpu intel-opencl-icd clinfo 

# Intel NPU Drivers
WORKDIR /tmp
RUN wget https://github.com/intel/linux-npu-driver/releases/download/v1.10.0/intel-driver-compiler-npu_1.10.0.20241107-11729849322_ubuntu24.04_amd64.deb \
    https://github.com/intel/linux-npu-driver/releases/download/v1.10.0/intel-fw-npu_1.10.0.20241107-11729849322_ubuntu24.04_amd64.deb \
    https://github.com/intel/linux-npu-driver/releases/download/v1.10.0/intel-level-zero-npu_1.10.0.20241107-11729849322_ubuntu24.04_amd64.deb && \
    dpkg -i *.deb && rm -f *.deb

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

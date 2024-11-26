# Base image
FROM ubuntu:24.04

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
    pip3 install --upgrade pip 

# Intel GPU Drivers
RUN wget -qO - https://repositories.intel.com/gpu/intel-graphics.key | \
  gpg --yes --dearmor --output /usr/share/keyrings/intel-graphics.gpg
RUN echo "deb [arch=amd64,i386 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/gpu/ubuntu noble client" | \
  tee /etc/apt/sources.list.d/intel-gpu-noble.list
RUN apt update -y
RUN apt install -y libze1 intel-level-zero-gpu intel-opencl-icd clinfo

# Intel NPU Drivers
WORKDIR /tmp
RUN wget https://github.com/intel/linux-npu-driver/releases/download/v1.10.0/intel-driver-compiler-npu_1.10.0.20241107-11729849322_ubuntu24.04_amd64.deb \
    https://github.com/intel/linux-npu-driver/releases/download/v1.10.0/intel-fw-npu_1.10.0.20241107-11729849322_ubuntu24.04_amd64.deb \
    https://github.com/intel/linux-npu-driver/releases/download/v1.10.0/intel-level-zero-npu_1.10.0.20241107-11729849322_ubuntu24.04_amd64.deb && \
    dpkg -i *.deb && rm -f *.deb

# OpenVINO GenAI 
RUN pip3 install -U --pre openvino-genai openvino openvino-tokenizers[transformers] \
	 --extra-index-url https://storage.openvinotoolkit.org/simple/wheels/nightly 
RUN pip3 install --extra-index-url https://download.pytorch.org/whl/cpu \
	"git+https://github.com/huggingface/optimum-intel.git" \
	"git+https://github.com/openvinotoolkit/nncf.git" "onnx<=1.16.1"

RUN pip3 install tabulate fire

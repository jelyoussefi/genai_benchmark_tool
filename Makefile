# Basic Settings
CURRENT_DIR := $(shell pwd)
CACHE_DIR := $(CURRENT_DIR)/.cache
DOCKER_IMAGE_NAME = genait_benchmark_tool

MODEL_NAME ?= meta-llama/Meta-Llama-3-8B
EXPORT_DIR := $(shell echo $(MODEL_NAME) | awk -F/ '{print $$2}')
PROMPT_FILE ?= user_prompt.txt

DEVICE ?= GPU

HF_TOKEN ?= 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

# Docker run options
DOCKER_RUN_OPTS = \
    -it --rm --privileged \
    -v /dev:/dev \
    -v $(CURRENT_DIR):/workspace \
    -v $(CACHE_DIR):/root/.cache \
    -w /workspace \
    -e http_proxy=$(HTTP_PROXY) \
    -e https_proxy=$(HTTPS_PROXY) \
    -e no_proxy=$(NO_PROXY) \
    -e EXPORT_DIR=$(EXPORT_DIR) \
    -e HF_HOME=/root/.cache \
    -e HF_TOKEN=$(HF_TOKEN) \
    $(DOCKER_IMAGE_NAME)

# Default target
default: run

# Build Docker image
build:
	@echo "Building Docker image $(DOCKER_IMAGE_NAME)..."
	@mkdir -p $(CACHE_DIR)
	@docker build . -t $(DOCKER_IMAGE_NAME) \
                --build-arg http_proxy=${HTTP_PROXY} \
                --build-arg https_proxy=${HTTPS_PROXY} \
                --build-arg no_proxy=${NO_PROXY}

# Reformat the model using Hugging Face transformers library
reformat_model: build
	@echo "Reformatting model $(MODEL_NAME) for proper pipeline structure..."
	@docker run $(DOCKER_RUN_OPTS) \
            python3 reformat_model.py --model_name $(MODEL_NAME)  --cache_dir /workspace/.cache

# Export the model using optimum-cli with original parameters
export_model: 
	@echo "Exporting model $(MODEL_NAME) to directory $(EXPORT_DIR)..."
	@docker run $(DOCKER_RUN_OPTS) \
            optimum-cli export openvino --task text-generation-with-past \
                --weight-format int4  \
                --cache_dir /root/.cache \
                --model  $(MODEL_NAME) $(EXPORT_DIR)

# Benchmark the model
run: export_model
	@echo "Benchmarking the model $(MODEL_NAME) with $(PROMPT_FILE) ..."
	@docker run $(DOCKER_RUN_OPTS) \
                ./benchmark_tool.py --model_dir $(EXPORT_DIR) \
                                --prompt $(PROMPT_FILE) \
                                --device $(DEVICE)

bash: build
	@docker run $(DOCKER_RUN_OPTS) bash


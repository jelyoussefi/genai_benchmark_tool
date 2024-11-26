# Basic Settings
CURRENT_DIR := $(shell pwd)
HOST_CACHE_DIR := $(CURRENT_DIR)/.cache
CACHE_DIR := /root/.cache
DOCKER_IMAGE_NAME := genait_benchmark_tool

MODEL_NAME ?= meta-llama/Meta-Llama-3-8B
OLLAMA_MODEL_NAME ?= llama3.2

EXPORT_DIR := $(shell echo $(MODEL_NAME) | awk -F/ '{print $$2}')
PROMPT_FILE ?= user_prompt.txt

DEVICE ?= GPU
USE_OLLAMA ?= True

ifeq ("$(DEVICE)","XPU")
	CACHE_DIR := /root/.ollama
endif
# Docker run options
DOCKER_RUN_OPTS = \
    -it --rm --privileged \
    -v /dev:/dev \
    -v $(CURRENT_DIR):/workspace \
    -v $(HOST_CACHE_DIR):$(CACHE_DIR) \
    -v $(HOST_CACHE_DIR):/var/lib/ollama/ \
    -w /workspace \
    -e http_proxy=$(HTTP_PROXY) \
    -e https_proxy=$(HTTPS_PROXY) \
    -e no_proxy=$(NO_PROXY) \
    -e EXPORT_DIR=$(EXPORT_DIR) \
    -e HF_HOME=$(CACHE_DIR) \
    -e HF_TOKEN=$(HF_TOKEN) \
    -e TOKENIZERS_PARALLELISM=true \
    -e OLLAMA_NUM_GPU=999 \
    -e ZES_ENABLE_SYSMAN=1 \
    $(DOCKER_IMAGE_NAME)

# Default target
default: run

# Build Docker image
build:
	@echo "Building Docker image $(DOCKER_IMAGE_NAME)..."
	@mkdir -p $(HOST_CACHE_DIR)
	@docker build . -t $(DOCKER_IMAGE_NAME) \
		--build-arg http_proxy=${HTTP_PROXY} \
		--build-arg https_proxy=${HTTPS_PROXY} \
		--build-arg no_proxy=${NO_PROXY}

# Export the model using optimum-cli with original parameters
export_model: build
	@echo "Exporting model $(MODEL_NAME) to directory $(EXPORT_DIR)..."
	@docker run $(DOCKER_RUN_OPTS) \
		optimum-cli export openvino \
			--task text-generation-with-past \
			--weight-format int4  \
			--cache_dir $(CACHE_DIR) \
			--model  $(MODEL_NAME) $(EXPORT_DIR)

# Benchmark the model
run: build
	@echo "Benchmarking the model..."
	@if [ "$(USE_OLLAMA)" = "True" ]; then \
		echo "Using Ollama model: $(OLLAMA_MODEL_NAME)"; \
		MODEL_NAME=$(OLLAMA_MODEL_NAME); \
	else \
		echo "Using Hugging Face model: $(MODEL_NAME)"; \
	fi; \
	docker run $(DOCKER_RUN_OPTS) \
		python3 ./benchmark_tool.py \
			--model_name $$MODEL_NAME \
			--model_dir $(EXPORT_DIR) \
			--prompt $(PROMPT_FILE) \
			--device $(DEVICE) \
			--use_ollama $(USE_OLLAMA)

bash: build
	@docker run $(DOCKER_RUN_OPTS) bash

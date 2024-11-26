
# GenAI Benchmark Tool

This project provides a Dockerized setup for exporting and benchmarking machine learning models using OpenVINO and `optimum-cli`. It also supports integration with Ollama for remote model serving.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Features](#features)
- [Usage](#usage)
  - [Building the Docker Image](#building-the-docker-image)
  - [Exporting the Model](#exporting-the-model)
  - [Benchmarking the Model](#benchmarking-the-model)
  - [Accessing the Container](#accessing-the-container)
- [Command-Line Arguments](#command-line-arguments)
- [Environment Variables](#environment-variables)
- [Customizations](#customizations)
- [Logging and Output](#logging-and-output)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites
- Docker installed and running.
- Access to the target model repository (e.g., Hugging Face).
- Valid Hugging Face token for private models.

---

## Features
- Export machine learning models to OpenVINO format using `optimum-cli`.
- Benchmark text-generation models with customizable prompts.
- Dual support for local (OpenVINO) and remote (Ollama) pipelines.
- Real-time token counting and performance metrics (e.g., inference time, tokens/s).
- Outputs results in a formatted table and saves the generated response to a file.

---

## Usage

### 1. Building the Docker Image
Build the Docker image for the benchmarking tool:
```bash
make build
```

### 2. Exporting the Model
Export a model to OpenVINO-compatible format:
```bash
make export_model
```

This will:
- Use the model specified in the `MODEL_NAME` variable.
- Save the exported model to a directory derived from the model name.

### 3. Benchmarking the Model
Run benchmarks on the exported model:
```bash
make run
```

This executes the `benchmark_tool.py` script with the following key steps:
- Loads the prompt file and prepends the system prompt.
- Depending on the `USE_OLLAMA` flag:
  - Uses the OpenVINO pipeline for local inference.
  - Initializes the Ollama server and performs inference remotely.
- Calculates performance metrics and outputs results in a tabular format.

Example usage with a specific prompt file:
```bash
make run PROMPT_FILE=my_prompt.txt
```

### 4. Accessing the Container
To manually access the container environment:
```bash
make bash
```

---

## Command-Line Arguments
The `benchmark_tool.py` script accepts the following arguments:

| Argument          | Description                                             | Default Value                |
|--------------------|---------------------------------------------------------|------------------------------|
| `model_dir`       | Directory containing the exported model.                | (Required)                   |
| `model_name`      | Name of the model (used when `USE_OLLAMA=True`).         | (None)                       |
| `prompt`          | Path to the user's prompt file.                         | (Required)                   |
| `system_prompt`   | System prompt prepended to the user's prompt.           | `"You are a helpful assistant."` |
| `device`          | Device for benchmarking (`CPU` or `GPU`).               | `GPU`                        |
| `output_file`     | File to save the generated response.                    | `answer.txt`                 |
| `use_ollama`      | Enable Ollama for remote model inferencing.             | `False`                      |

Example:
```bash
python3 benchmark_tool.py --model_dir exported_model --prompt user_prompt.txt --device GPU --use_ollama True
```

---

## Environment Variables
The following environment variables are used:

| Variable               | Description                                       | Default Value              |
|------------------------|---------------------------------------------------|----------------------------|
| `MODEL_NAME`           | Model to export and benchmark.                    | `meta-llama/Meta-Llama-3-8B` |
| `PROMPT_FILE`          | Input file containing the prompts.                | `user_prompt.txt`          |
| `DEVICE`               | Device for benchmarking (`CPU` or `GPU`).         | `GPU`                      |
| `USE_OLLAMA`           | Whether to enable Ollama integration.             | `True`                     |
| `HTTP_PROXY`           | Proxy for HTTP connections.                       | (None)                     |
| `HTTPS_PROXY`          | Proxy for HTTPS connections.                      | (None)                     |
| `NO_PROXY`             | Bypass proxy for specific domains.                | (None)                     |

---

## Customizations
- Modify `MODEL_NAME` and `PROMPT_FILE` to test different models and inputs.
- Adjust `DEVICE` to switch between CPU and GPU.
- Customize Docker run options by editing the `DOCKER_RUN_OPTS` variable.
- Change the `system_prompt` to provide context-specific instructions for the assistant.

---

## Logging and Output
- **Generated Responses**: Saved to `answer.txt` (or a custom file specified via `output_file`).
- **Benchmark Results**: Printed in a formatted table, including metrics like inference time and tokens/s.
- **Ollama Logs**: Saved to `ollama.log` when Ollama is enabled.

---

## Troubleshooting
1. **Model Export Errors**:
   Ensure the `HF_TOKEN` is set and you have access to the specified model.

2. **Docker Build Issues**:
   Verify your proxy settings and Docker installation.

3. **GPU Detection Issues**:
   Ensure your system supports GPU pass-through in Docker and has the necessary drivers installed.

4. **Prompt File Not Found**:
   Verify the path to the `PROMPT_FILE` and ensure it contains the necessary text.

---

## License
This project is licensed under the MIT License.

# GenAI Benchmark Tool

The GenAI Benchmark Tool is designed to evaluate and benchmark AI models efficiently. It uses Makefile commands for simplified operations and Docker for isolated execution.

## Prerequisites

Before using this tool, ensure the following are installed:

- [Docker](https://www.docker.com/)
- [Make](https://www.gnu.org/software/make/)

## Environment Variables

The following environment variables are used for configuration:

| Variable     | Description                                  | Default Value       |
|--------------|----------------------------------------------|---------------------|
| `MODEL_NAME` | Name of the AI model to benchmark            | `gpt-3.5-turbo`     |
| `PROMPT_FILE`| Path to the file containing prompts for evaluation | `prompts.txt`    |
| `DEVICE`     | Device to run the model on (`CPU`, `GPU`, `NPU`) | `CPU`           |
| `HF_TOKEN`   | Hugging Face API token for model access      | `None`              |

You can override these variables directly when running the `make` commands.

## Usage

### Makefile Commands

Here are the main commands available in the Makefile:

| Command          | Description                                                             |
|------------------|-------------------------------------------------------------------------|
| `make build`     | Builds the Docker image for the benchmark tool.                        |
| `make run`       | Runs the benchmark using the specified configuration.                  |
| `make export_model` | Exports a Hugging Face model to OpenVINO format.                    |
| `make clean`     | Cleans up any temporary or generated files.                            |

### How to Run

1. **Build the Docker Image**  
   Run the following command to build the Docker image:
   ```bash
   make build

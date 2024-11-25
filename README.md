# GenAI Benchmark Tool

The GenAI Benchmark Tool is designed to evaluate and benchmark AI models efficiently. This tool leverages Docker and Makefile to ensure a seamless setup process and reproducible results.

## Prerequisites

Before using this tool, ensure the following are installed:

- [Docker](https://www.docker.com/)
- [Make](https://www.gnu.org/software/make/)

## Setup and Configuration

### Environment Variables

The tool uses the following environment variables for configuration, all defined in the `Makefile`:

- `MODEL_NAME`: The name of the AI model to benchmark (default: `gpt-3.5-turbo`).
- `PROMPT_FILE`: Path to the file containing the prompts for evaluation (default: `prompts.txt`).
- `DEVICE`: Device to run the model on, e.g., `cpu` or `cuda` (default: `cpu`).

These variables can be overridden at runtime by passing them directly to the `make` command.

## Usage

### Build the Docker Image

To build the Docker image, run:

```bash
make build
```

### Run the Benchmark

To execute the benchmark, use:

```bash
make run
```

### Override Environment Variables

You can override the default environment variables by appending them to the `make` command. For example:

```bash
make run MODEL_NAME=gpt-4 PROMPT_FILE=custom_prompts.txt DEVICE=cuda
```

### Clean Up

To remove any generated files or clean the environment, run:

```bash
make clean
```

## Project Structure

```plaintext
genai_benchmark_tool-main/
├── Dockerfile           # Docker configuration file
├── Makefile             # Contains commands and environment variables
├── main.py              # Main script to run the benchmark
├── prompts.txt          # Default file for prompts
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables configuration (optional)
└── README.md            # Project documentation
```

## Customization

Feel free to modify the `PROMPT_FILE` to include your own set of prompts or update `MODEL_NAME` to benchmark different models.

## Troubleshooting

- Ensure Docker is running and accessible from the command line.
- Check for permissions to access GPU devices if running on `cuda`.
- Validate the paths and contents of your prompt files.

## License

This project is licensed under the [MIT License](LICENSE).

## Contributions

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or features.

---

Happy benchmarking!

# Makefile for Docovert

export PYPANDOC_PANDOC=$(which pandoc)

.PHONY: run run-docker build setup format

# Run the server
run:
	@echo "Running Docovert..."
	uv run flask --app flaskr run --debug

# Run the server with Docker
run-docker:
	@echo "Running Docovert with Docker..."
	docker run -p 8080:8080 -d nhefner/docovert

# Build Docker image
build:
	@echo "Building Docker image..."
	docker build -t nhefner/docovert:latest .

# Install dependencies and tools
setup:
	@echo "Installing Python dependencies..."
	uv sync

	@echo "Installing npm dependencies..."
	npm install

	@echo "Done with setup."

# Format Python code
format:
	@echo "Running ruff..."
	uv run ruff format

	@echo "Running Prettier..."
	npx prettier . --write

	@echo "Formatting complete."

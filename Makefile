# Makefile for Docovert

.PHONY: format setup run

# Run the server
run:
	@echo "Running Docovert..."
	.venv/bin/flask --app main run

# Install dependencies and tools
setup:
	@echo "Installing Python dependencies..."
	uv sync

	@echo "Installing npm dependencies..."
	npm install

	@echo "Done with setup."

# Format Python code
format:
	@echo "Running isort..."
	./.venv/bin/isort .

	@echo "Running autoflake..."
	./.venv/bin/autoflake --in-place --remove-all-unused-imports --recursive .

	@echo "Running black formatter..."
	./.venv/bin/black .

	@echo "Running Prettier..."

	@echo "Formatting complete."
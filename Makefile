# Makefile for Docovert

.PHONY: format setup run

# Run the server
run:
	@echo "Running Docovert..."
	uv run flask --app flaskr run --debug

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
	uv run isort .

	@echo "Running autoflake..."
	uv run autoflake --in-place --remove-all-unused-imports --recursive .

	@echo "Running black formatter..."
	uv run black .

	@echo "Running Prettier..."
	npx prettier . --write

	@echo "Formatting complete."
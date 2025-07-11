.PHONY: help install run dev test clean setup check-env

# Default target
help:
	@echo "🍨 Jirato - AI-Powered JIRA Ticket Creator"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install dependencies with uv"
	@echo "  make setup      - Set up environment file"
	@echo "  make check-env  - Check environment variables"
	@echo "  make run        - Run the application"
	@echo "  make dev        - Run with auto-reload"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean up cache files"
	@echo "  make help       - Show this help message"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	uv sync

# Set up environment file
setup:
	@echo "⚙️  Setting up environment..."
	@if [ ! -f .env ]; then \
		echo "JIRA_TOKEN=your_jira_token_here" > .env; \
		echo "OLLAMA_REMOTE_HOST=http://ollama.hgi.sanger.ac.uk:11434" >> .env; \
		echo "✅ Created .env file"; \
		echo "⚠️  Please edit .env and add your JIRA_TOKEN"; \
	else \
		echo "✅ .env file already exists"; \
	fi

# Check environment variables
check-env:
	@echo "🔍 Checking environment variables..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found!"; \
		echo "Run 'make setup' to create it"; \
		exit 1; \
	fi
	@. .env && \
	if [ -z "$$JIRA_TOKEN" ] || [ "$$JIRA_TOKEN" = "your_jira_token_here" ]; then \
		echo "❌ JIRA_TOKEN not set or still default value"; \
		echo "Please edit .env and add your JIRA_TOKEN"; \
		exit 1; \
	else \
		echo "✅ Environment variables loaded successfully"; \
		echo "🔗 Ollama host: $${OLLAMA_REMOTE_HOST:-http://ollama.hgi.sanger.ac.uk:11434}"; \
	fi

# Run the application
run: check-env
	@echo "🎫 Starting Jirato Web App..."
	@echo "🚀 Server will be available at http://localhost"
	@echo "Press Ctrl+C to stop"
	@echo ""
	uv run python app.py

# Run with auto-reload for development
dev: check-env
	@echo "🔄 Starting Jirato in development mode..."
	@echo "🚀 Server will be available at http://localhost"
	@echo "📝 Auto-reload enabled"
	@echo "Press Ctrl+C to stop"
	@echo ""
	uv run uvicorn app:app --host 0.0.0.0 --port 80 --reload

# Run tests
test:
	@echo "🧪 Running tests..."
	@echo "⚠️  No tests configured yet"
	@echo "Add your test files and update this target"

# Clean up cache files
clean:
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Full setup (install + setup)
full-setup: install setup
	@echo "🎉 Full setup complete!"
	@echo "Next steps:"
	@echo "1. Edit .env and add your JIRA_TOKEN"
	@echo "2. Run 'make run' to start the application" 
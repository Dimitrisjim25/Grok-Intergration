# Stage 1: Build the virtual environment
FROM python:3.10-slim AS builder

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies needed for pyaudio
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    libasound-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies into the venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Stage 2: Final production image
FROM python:3.10-slim

# Install only runtime dependencies for pyaudio
RUN apt-get update && apt-get install -y --no-install-recommends \
    portaudio19-dev \
    libasound-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Set working directory
WORKDIR /home/appuser/app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set the path to use the venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application source code
COPY --chown=appuser:appuser . .

# Expose environment variables (API_KEY should be passed during `docker run`)
ENV LOG_LEVEL="INFO"


# Healthcheck to verify the main script is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ps aux | grep -q "[p]ython src/tesla_grok_integration.py" || exit 1

# Command to run the application
CMD ["python", "src/tesla_grok_integration.py"]

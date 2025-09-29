# Base Python image
FROM python:3.11-slim

# Install Java + unzip + curl
RUN apt-get update && apt-get install -y openjdk-17-jre-headless curl unzip \
    && rm -rf /var/lib/apt/lists/*

# Environment for PMD
ENV PMD_VERSION=7.17.0
ENV PMD_HOME=/opt/pmd
ENV PATH=$PMD_HOME/bin:$PATH

# Download & extract PMD
RUN mkdir -p $PMD_HOME \
    && curl -L -o /tmp/pmd.zip https://github.com/pmd/pmd/releases/download/pmd_releases/${PMD_VERSION}/pmd-bin-${PMD_VERSION}.zip \
    && unzip /tmp/pmd.zip -d /opt \
    && mv /opt/pmd-bin-${PMD_VERSION}/* $PMD_HOME \
    && rm /tmp/pmd.zip

# Copy Python code
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Expose default port
EXPOSE 5000

# Start Vercel serverless entrypoint
CMD ["vercel", "dev"]

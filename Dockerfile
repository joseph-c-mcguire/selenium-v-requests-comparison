FROM python:3.11.9-slim

WORKDIR /app
COPY . .

# Install dependencies and Google Chrome for Selenium
RUN apt-get update && apt-get install -y wget gnupg unzip && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    python -m pip install --upgrade pip && \
    pip install .

# Set entrypoint to run the comparison tool
CMD ["python", "-m", "selenium_v_requests_comparison"]

FROM debian:13-slim

# install prerequisites: git curl
RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl ca-certificates nano \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/\*

WORKDIR /app

# shared data folder
VOLUME ["/app/data"]

ARG DATAWAREHOUSE
ARG USE_TERRAFORM

# COPY . .

COPY .env .

# COPY .bruin.yml .
COPY pipeline .

COPY .streamlit  /app/.streamlit
copy app.py .

COPY start_app.sh .

CMD ["bash", "start_app.sh"]

#!/bin/bash
echo
echo '1. STARTING WORKFLOW'
echo

# echo '1.1. TERRAFORM?'
# bash terraform-setup.sh
# sleep 1

echo
echo '1.2. Bruin pipeline needs git init'
git init

export PATH="$PATH:/root/.local/bin"

echo
echo '1.3. Installing Bruin'
curl -LsSf https://getbruin.com/install/cli | sh
bruin --version

echo
echo '1.4. Installing UV'
curl -LsSf https://astral.sh/uv/install.sh | sh

echo
echo '1.5. Installing Streamlit'
# cd pipeline
uv add streamlit && uv run streamlit --version
# cd /app


echo
echo '2. Starting Bruin pipeline...'
echo
bruin run pipeline.yml --start-date 2022-01-01 --end-date 2026-03-31
sleep 5

echo
echo '3. Starting Streamlit app...'
echo
uv run streamlit run app.py

sleep 5

---
title: Finance RL Trading Environment
emoji: 📈
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - pytorch
  - finance
  - reinforcement-learning
---

# Finance RL Trading Environment

This project implements an Agentic Reinforcement Learning environment for automated stock trading, developed for the Meta x Hugging Face OpenEnv Hackathon. It utilizes historical market data and leverages **DeepSeek-R1** via the Hugging Face Router to provide high-fidelity rewards based on fundamental and technical analysis.

## 📂 Project Structure

- **`finance_rl_proj/server/`**: Contains the core environment logic (`finance_rl_proj_environment.py`) and the FastAPI server entry point (`app.py`).
- **`inference.py`**: The mandatory entry point for automated evaluation. It executes the trading agent and outputs structured logs.
- **`models.py`**: Pydantic models for strictly typed Actions and Observations.
- **`stock_analysis.py`**: Integration with the OpenAI SDK to perform LLM-based grading of trading decisions.
- **`historic_data.py`**: Data acquisition layer using `yfinance`.
- **`openenv.yaml`**: Manifest file defining environment tasks and metadata.
- **`Dockerfile`**: Root-level container definition for reproducible builds.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have the following environment variables set in your Hugging Face Space or local `.env` file:
- `HF_TOKEN`: Your Hugging Face API token.
- `API_BASE_URL`: `https://api-inference.huggingface.co/v1/`
- `MODEL_NAME`: e.g., `deepseek-ai/DeepSeek-R1-Distill-Qwen-32B`
- `STOCK_NAME`: Default stock ticker (e.g., `AAPL`).

### 2. Local Installation
```bash
python -m venv rl_env
source rl_env/bin/activate
pip install -e.

### 3. Running the Environment
Start the OpenEnv server:
```bash
uvicorn finance_rl_proj.server.app:app --host 0.0.0.0 --port 8000

### 4.Running Inference (Validation)
Execute the mandatory inference script to verify logging compliance:
```bash
python inference.py

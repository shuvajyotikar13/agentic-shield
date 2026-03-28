# 🛡️ Agentic Shield: Real-Time Semantic Security

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?logo=redis&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache_Kafka-231F20?logo=apache-kafka&logoColor=white)

A high-performance, event-driven architecture demonstrating how to use **Redis Vector Search** as a sub-10ms semantic firewall for autonomous AI agents consuming **Apache Kafka** streams.

## 📖 The "Agentic Tax" Problem
When running autonomous agents at scale (e.g., in a SOC), every decision loop is expensive. If your agents consume a firehose of telemetry and commands from Kafka, sending every event to a "Guardrail LLM" for security validation introduces massive latency, causing Kafka consumer lag to spiral. 

**Traditional WAFs (Regex) fail** because prompt injections change lexically while maintaining the same semantic intent (e.g., *"Ignore instructions"* vs. *"Disregard rules"*).

## 💡 The Solution: A Semantic Firewall
This repository demonstrates an inline L1 Brain for AI agents. By embedding incoming Kafka payloads locally and performing a K-Nearest Neighbors (KNN) vector search against a Redis database of known threats, we calculate the *intent* of a prompt. Malicious packets are dropped in **<10ms**, bypassing the expensive LLM entirely and keeping consumer lag at zero.

## 🏗️ Architecture

1. **Ingestion (Apache Kafka):** Buffers incoming streaming events and commands.
2. **The Fast Path (Redis Vector Search):** Intercepts the event. If the semantic distance (Cosine Similarity) is `< 0.65` against a known attack cluster, the packet is dropped immediately.
3. **The Slow Path (Agent/LLM):** If the prompt is benign, it clears the firewall and is forwarded to the AI agent for standard processing and action.

## 📂 Repository Structure

```text
agentic-shield-demo/
├── docker-compose.yml      # Local Kafka & Redis Stack infrastructure
├── requirements.txt        # Python dependencies
├── src/
│   ├── setup_redis.py      # Initializes the vector index and seeds diverse attack clusters
│   ├── agent_shield.py     # Core Redis vector search and semantic threshold logic
│   ├── consumer.py         # The Agent: Consumes Kafka topics and triggers the shield
│   └── producer.py         # The Attacker: Simulates 100 realistic SOC events & injections
```
## 🚀 Quick Start (Demo)
This demo uses docker-compose to spin up a local Kafka broker and Redis Stack (required for RediSearch/Vector Search).

1. **Start the Infrastructure**
   
```bash
docker-compose up -d
```
2.  **Install Dependencies**
(It is recommended to use a virtual environment)

```bash
source .venv/bin/activate
pip install -r requirements.txt
```
3.  **Seed the Redis Vector Database**

Creates the all-MiniLM-L6-v2 index and loads a diverse cluster of baseline prompt injection attacks into memory to train the firewall.

```bash
python src/setup_redis.py
```
5. **Launch the Threat Simulation (Producer)**
In a second terminal window, run the threat simulation engine. This script fires 100 realistic events into Kafka, mixing benign SOC queries, random IT noise, and mutated zero-day prompt injections.

```bash
python src/producer.py
```

## 📊 What to Expect in the Logs
Watch the logs in your Consumer terminal. You will see:

Benign Traffic (The Slow Path): Standard SOC queries will register a high semantic distance (e.g., 0.88+), safely passing the firewall to be processed by the Agent.

Mutated Attacks (The Fast Path): When a zero-day injection hits the stream, Redis will mathematically recognize the intent (scoring < 0.65 distance) and drop the payload in milliseconds, flashing a red [BLOCKED] alert.

## 🛠️ Tech Stack
Streaming: Apache Kafka / Confluent (confluent-kafka)

Context & Memory: Redis Stack (RediSearch)

Embeddings: sentence-transformers (all-MiniLM-L6-v2)

Compute: Python (Designed for Serverless deployments like Google Cloud Run)

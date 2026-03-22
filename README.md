# Agent OS: OpenClaw-Style Two-Agent System with Local Models

## Overview

This project implements a **two-agent OpenClaw-style pipeline** using a locally hosted, quantized LLM (**Qwen2.5-7B via Ollama**) to simulate a banking voice AI system.

The system consists of:

* **Agent 1 (Responder):** Generates responses to borrower queries
* **Agent 2 (Validator):** Validates responses against safety and compliance rules

The goal is to evaluate:

* **End-to-end latency**
* **Agent-level performance**
* **Reliability of local quantized models**

---

## System Architecture

```
User Query
   ↓
Agent 1 (Response Generation)
   ↓
Agent 2 (Validation / Compliance Check)
   ↓
Final Output + Metrics
```

---

## Model Setup

* Model: `Qwen2.5-7B (quantized)`
* Runtime: **Ollama**
* Hardware: RTX 4060 (8GB VRAM)
* No external API calls — fully local inference

---

## Agents

### Agent 1 — Borrower Assistant

* Generates responses to user queries
* Constrained to:

  * Avoid false promises
  * Avoid hallucinated numbers
  * Maintain professional tone

---

### Agent 2 — Validator

Validates responses against three hardcoded rules:

1. No false promises
2. No hallucinated numerical values
3. No policy violations

Returns:

* `valid: true/false`
* `issues: explanation`

---

## Evaluation Setup

* 10 diverse borrower queries (including edge cases)
* Each query passes through both agents
* Metrics collected:

  * Total latency
  * Agent-wise latency
  * Percentiles (p50, p95)

---

## Results

| Metric         | Value |
| -------------- | ----- |
| p50 latency    | 3.74s |
| p95 latency    | 8.96s |
| avg latency    | 4.83s |
| Agent1 latency | 3.86s |
| Agent2 latency | 0.97s |

---

## Key Insights

* Response generation dominates total latency (~80%), making it the primary bottleneck.
* The validation agent adds only ~20% overhead while improving safety.
* High p95 latency (~8.96s) indicates variability in response time, likely due to longer token generation and complex queries.
* The system is not suitable for strict real-time applications but works for asynchronous pipelines.
* Validation is significantly cheaper than generation, making multi-agent safety layers feasible even on constrained hardware.

---

## What Broke

* Agent 1 occasionally returned invalid JSON outputs.
* Validator failed to catch subtle or “soft” hallucinations.
* Latency spikes were observed for longer or ambiguous queries.
* Some responses passed validation despite being overly generic or incomplete.

---

## Fixes Implemented

* Added JSON parsing fallback for robustness.
* Strengthened prompt constraints for both agents.
* Reduced generation length to stabilize latency.
* Introduced structured outputs to improve validation reliability.

---

## Limitations of Local Models

* Quantized models show reduced reliability in strict rule-following tasks.
* Hallucination detection is inconsistent without stronger supervision.
* Latency is significantly higher than API-based systems.
* Performance degrades with longer context or ambiguous inputs.

---

## Future Improvements

* Replace validator LLM with hybrid rule-based + lightweight model system.
* Introduce caching for repeated queries.
* Use vLLM for improved throughput and batching.
* Fine-tune model for domain-specific (banking) behavior.
* Add confidence scoring and rejection mechanisms.

---

## Conclusion

This project demonstrates that **multi-agent safety pipelines are feasible on local hardware**, but highlights a key tradeoff:

> Adding validation improves reliability with minimal overhead, but generation latency remains the dominant bottleneck.

This reinforces the need for **hybrid architectures** in production systems combining:

* fast inference
* rule-based safeguards
* and lightweight validation layers

---

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

---



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
* **Impact of optimization strategies on latency (especially p95)**

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
  * Produce concise outputs (optimized version)

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

# 🔬 Optimization Experiment

To reduce tail latency (p95), we introduced:

* Token limit (`num_predict`)
* Concise prompting
* Reduced validator input size

---

## 📊 Latency Comparison (Before vs After)

| Metric         | Before Optimization | After Optimization |
| -------------- | ------------------- | ------------------ |
| p50 latency    | 3.74s               | ~3.2s              |
| p95 latency    | 8.96s               | ~5.5–6.0s          |
| avg latency    | 4.83s               | ~4.0s              |
| Agent1 latency | 3.86s               | ↓ reduced          |
| Agent2 latency | 0.97s               | slightly reduced   |

---

## 🧠 Key Observation from Experiment

> Tail latency is primarily driven by **token generation variability**, not compute throughput.

---

## ⚙️ Optimization Techniques Applied

| Technique                   | Impact                           |
| --------------------------- | -------------------------------- |
| Token limit (`num_predict`) | Reduced long outputs → lower p95 |
| Prompt compression          | Reduced generation variability   |
| Shortened validator input   | Reduced validation latency       |
| Lower temperature           | Improved consistency             |

---

## Results (Baseline)

| Metric         | Value |
| -------------- | ----- |
| p50 latency    | 3.74s |
| p95 latency    | 8.96s |
| avg latency    | 4.83s |
| Agent1 latency | 3.86s |
| Agent2 latency | 0.97s |

---

## Notebook Findings (New .ipynb Run)

Source used: `results.json` generated from the newly added notebook workflow (`Ollama_server_run.ipynb`).

Run profile:

* Total evaluated queries: 12
* Validator outcomes: 11 compliant, 1 non-compliant
* Agent1 risk flag count: 3

| Metric         | Notebook Value |
| -------------- | -------------- |
| p50 latency    | 4.00s          |
| p95 latency    | 4.80s          |
| avg latency    | 3.95s          |
| Agent1 latency | 2.94s          |
| Agent2 latency | 1.01s          |

---

## Comparison (Baseline vs Notebook Findings)

| Metric         | Baseline | Notebook | Delta (Notebook - Baseline) |
| -------------- | -------- | -------- | --------------------------- |
| p50 latency    | 3.74s    | 4.00s    | +0.26s (+7.0%)             |
| p95 latency    | 8.96s    | 4.80s    | -4.16s (-46.5%)            |
| avg latency    | 4.83s    | 3.95s    | -0.88s (-18.3%)            |
| Agent1 latency | 3.86s    | 2.94s    | -0.92s (-23.9%)            |
| Agent2 latency | 0.97s    | 1.01s    | +0.04s (+4.1%)             |

Notes:

* The two result sets were run with different sample sizes (baseline: 10 queries, notebook run: 12 queries), so trend comparison is more reliable than strict absolute ranking.
* The biggest gain in the notebook run is tail latency (p95), while median latency (p50) is slightly higher.

---

## Key Insights

* Response generation dominates total latency (~80%), making it the primary bottleneck.
* The validation agent adds only ~20% overhead while improving safety.
* High p95 latency (~8.96s) indicates variability in response time due to token generation.
* Optimization significantly reduces tail latency without major accuracy loss.
* Validation is computationally cheap compared to generation.

---

## Tradeoff Analysis

| Factor      | Without Validator | With Validator |
| ----------- | ----------------- | -------------- |
| Latency     | Lower             | Higher (+20%)  |
| Safety      | Low               | High           |
| Reliability | Unstable          | Improved       |

---

## Example Failure Case

**Query:**
"Can you waive my EMI penalty?"

**Agent 1 Output:**
"Yes, we can waive your penalty."

**Validator Output:**
`VALID ❌`

**Issue:**
Validator failed to detect a false promise.

---

## What Broke

* Agent 1 occasionally returned invalid JSON outputs
* Validator missed subtle hallucinations
* Significant latency spikes for long responses
* Some unsafe responses passed validation

---

## Fixes Implemented

* JSON parsing fallback
* Stronger prompt constraints
* Token limit to control output length
* Structured outputs for consistency

---

## Limitations of Local Models

* Quantized models struggle with strict rule enforcement
* Validator reliability is not guaranteed
* Latency unsuitable for real-time voice pipelines
* Performance sensitive to prompt design

---

## Production Risks

* Unsafe responses may pass validation
* High p95 latency impacts user experience
* Lack of domain grounding leads to hallucinations

---

## Future Improvements

* Hybrid validator (rule-based + LLM)
* Response caching for repeated queries
* Use vLLM for batching and throughput
* Fine-tune for banking domain
* Add confidence scoring + rejection mechanism

---

## Conclusion

This project demonstrates that **multi-agent safety pipelines are feasible on local hardware**, but highlights a key tradeoff:

> Safety layers are computationally cheap, but their effectiveness depends heavily on model reliability.

> Tail latency is dominated by token generation variability, making output control critical for production systems.

---

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

---

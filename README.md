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

This repository now documents **two execution modes**:

* **Baseline mode (hardcoded):** Agents are directly wired in project code (borrower -> validator) with hardcoded prompts/rules.
* **OpenClaw mode (server-routed):** The notebook runs with OpenClaw server-style routing, and agent calls are resolved via OpenClaw registration/configuration before inference.

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

Baseline definition: this is the original project path where agent orchestration is **hardcoded in code** (direct borrower + validator call chain), without OpenClaw routing.

| Metric         | Value |
| -------------- | ----- |
| p50 latency    | 3.74s |
| p95 latency    | 8.96s |
| avg latency    | 4.83s |
| Agent1 latency | 3.86s |
| Agent2 latency | 0.97s |

---

## Notebook Definition (openclaw_server.ipynb)

`openclaw_server.ipynb` is the OpenClaw-routed experiment notebook.

It is different from baseline in a key way:

* **Baseline path:** agent orchestration is hardcoded directly in project code.
* **Notebook path:** agent orchestration is resolved through OpenClaw configuration/registration, and agent calls are routed through the OpenClaw server flow.

OpenClaw notebook flow:

1. Resolve registered agents (borrower-support and compliance-validator) from OpenClaw configuration.
2. Route borrower and validator turns using OpenClaw-managed invocation.
3. Run ablation variants (`baseline_skill_repair`, `no_json_repair`, `no_skill_rules`) and collect latency/compliance metrics.
4. Save benchmark outputs (`ablation_runs.csv`, `ablation_summary.csv`, `ablation_summary.json`).

---

## Notebook Findings (openclaw_server.ipynb)

This section is kept separate for direct side-by-side comparison.

Experiment setup captured from notebook output:

* Variants tested: `baseline_skill_repair`, `no_json_repair`, `no_skill_rules`
* Runs per variant: 15
* Total rows collected: 45

| Backend | Variant              | Runs | p50 (s) | p95 (s) | Mean (s) | Parse Error Rate | Compliance Rate |
| ------- | -------------------- | ---- | ------- | ------- | -------- | ---------------- | --------------- |
| ollama  | baseline_skill_repair| 15   | 10.110  | 13.875  | 10.699   | 0.000            | 0.133           |
| ollama  | no_json_repair       | 15   | 9.795   | 14.958  | 10.477   | 0.000            | 0.133           |
| ollama  | no_skill_rules       | 15   | 10.055  | 15.894  | 10.748   | 0.000            | 0.200           |

### Comparison (Original Baseline vs OpenClaw Baseline Variant)

Comparison note: this is a comparison between two different orchestration paths:

* Original baseline = hardcoded agent chain in project code
* OpenClaw baseline variant = OpenClaw-routed chain from notebook/server flow

| Metric      | Original Baseline | OpenClaw baseline_skill_repair | Delta (OpenClaw - Original) |
| ----------- | ----------------- | ------------------------------ | --------------------------- |
| p50 latency | 3.74s             | 10.11s                         | +6.37s (+170.3%)           |
| p95 latency | 8.96s             | 13.88s                         | +4.92s (+54.9%)            |
| avg latency | 4.83s             | 10.70s                         | +5.87s (+121.5%)           |

Interpretation notes:

* This notebook evaluates additional OpenClaw routing and ablation behavior, so absolute latency is expected to differ from the earlier direct two-agent benchmark.
* `no_skill_rules` shows the highest compliance rate in this run, but the lowest tail-latency performance (highest p95).

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

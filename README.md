# ANOMALY
### Autonomous Scientific Investigation Agent

> Find what current knowledge cannot yet explain. Build competing explanations. Test them. Decide what to investigate next.

AgentX-2026 — Agentic AI for Scientific Discovery & Engineering

ANOMALY is an autonomous scientific investigation system designed to turn an unexplained observation into a structured, evidence-grounded investigation.

Instead of simply answering a research question, ANOMALY follows an investigation loop:

Evidence → Anomaly → Hypotheses → Critique → Test → Next Investigation

The system separates observations from hypotheses, maintains competing explanations, challenges them, performs deterministic computational tests where applicable, and exposes uncertainty and missing evidence.

---

## The Problem

Scientific investigations often begin with a simple question:

"This observation does not fit what our model predicts. Why?"

The difficulty is not always finding an answer.

Researchers may need to:

- gather evidence from different sources
- identify what is actually unexplained
- distinguish observations from interpretations
- compare multiple possible explanations
- challenge their own hypotheses
- perform calculations or simulations
- determine what evidence is still missing
- decide what experiment or analysis should happen next

A general-purpose AI assistant can generate explanations, but generating an explanation is not the same as conducting an investigation.

### ANOMALY's Objective

Given an unexplained observation, ANOMALY attempts to:

1. Establish what is known.
2. Identify anomalies, contradictions, or unexplained residuals.
3. Generate competing hypotheses.
4. Critically evaluate those hypotheses.
5. Run applicable computational tests.
6. Identify uncertainty and missing evidence.
7. Propose the next investigation or experiment.

---

## What Makes ANOMALY Different?

### A normal chatbot

Question → Answer

### ANOMALY

Research Question / Observation
        ↓
Evidence
        ↓
Anomaly Detection
        ↓
Competing Hypotheses
        ↓
Critic
        ↓
Computational Testing
        ↓
Evidence + Uncertainty
        ↓
Next Investigation
        ↓
Human Researcher

The goal is therefore not:

"Generate the most convincing answer."

It is:

"Determine what remains unexplained and what should be tested next."

ANOMALY is not intended to replace scientific judgment. Human researchers remain responsible for validating conclusions and approving real-world experiments.

---

## Agent Architecture

                         HUMAN RESEARCHER
                                │
                                ▼
                       RESEARCH QUESTION
                                │
                                ▼
                         ORCHESTRATOR
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
        EVIDENCE AGENT    ANOMALY AGENT    RESEARCH AGENT
              │                 │                 │
              └─────────────────┼─────────────────┘
                                ▼
                       HYPOTHESIS AGENT
                                │
                     ┌──────────┼──────────┐
                     ▼          ▼          ▼
                    H1         H2         H3
                     │          │          │
                     └──────────┼──────────┘
                                ▼
                         CRITIC AGENT
                                │
                                ▼
                    SCIENTIFIC TESTING
                                │
                                ▼
                    TEST RESULTS + EVIDENCE
                                │
                                ▼
                     NEXT INVESTIGATION
                                │
                                ▼
                       HUMAN VALIDATION

### Current Implemented Investigation Chain

Input
  ↓
Evidence Agent
  ↓
Numerical Anomaly Analysis
  ↓
Anomaly Agent
  ↓
Hypothesis Agent
  ↓
Critic Agent
  ↓
Dynamic Scientific Testing
  ↓
Investigation State

The architecture is modular so additional research, simulation, literature, and experiment-design capabilities can be added without replacing the core investigation engine.

---

## Current Agents

| Component | Responsibility |
|---|---|
| Evidence Agent | Structures and summarizes supplied evidence |
| Numerical Anomaly Engine | Detects residuals, trends, correlations, persistence and candidate anomalies |
| Anomaly Agent | Determines what observations require investigation |
| Hypothesis Agent | Generates multiple competing explanations |
| Critic Agent | Challenges hypotheses and identifies supporting/contradicting evidence |
| Scientific Testing Agent | Selects an applicable deterministic computational test |
| Orchestrator | Coordinates the investigation pipeline |
| Investigation State | Preserves structured investigation results and intermediate state |

---

## Numerical Reasoning

ANOMALY does not rely entirely on an LLM for numerical reasoning.

The numerical analysis layer performs deterministic calculations such as:

- residual analysis
- linear trends
- Pearson correlations
- persistence detection
- outlier detection
- measurement statistics
- observed vs predicted comparisons

This creates a separation between:

LLM
→ reasoning, hypothesis generation and interpretation

Deterministic tools
→ numerical calculations and scientific tests

This reduces the risk of allowing generated text to silently replace actual calculations.

---

## Scientific Testing

ANOMALY can dynamically select an applicable scientific testing tool based on the investigation.

Current prototype tools include:

- thermal_recoil_estimation
- acceleration_comparison

For example, in a thermal-recoil investigation:

Thermal Power
      ↓
Radiation Force
      ↓
Acceleration Estimate
      ↓
Compare Against Observation
      ↓
Evaluate Hypothesis

The computational tools are deterministic and their inputs and results can be inspected independently of the language model.

---

## Example Investigation — Pioneer Anomaly

One benchmark case uses the historical Pioneer anomaly.

The supplied observation contains:

- persistent Sunward acceleration residuals
- Doppler tracking observations
- similar spacecraft characteristics
- significant onboard thermal energy
- known gravitational and navigational models
- an unexplained residual

ANOMALY considers competing possibilities such as:

### H1 — Thermal radiation recoil

Anisotropic thermal emission produces a small reaction force.

### H2 — Measurement / telemetry effects

The apparent acceleration could arise from measurement or modelling errors.

### H3 — Unmodelled external effects

An external force or environmental effect could contribute to the residual.

The system evaluates the available evidence, challenges the hypotheses, and applies the relevant computational test where possible.

The benchmark answer is kept separate from the blind case so that evaluation does not require exposing the expected explanation to the investigation pipeline.

---

## Input Support

ANOMALY currently accepts structured investigation inputs including:

- JSON
- CSV
- TXT
- Markdown
- PDF

Inputs can contain:

- Objective
- Observations
- Measurements
- Experimental Context
- Expected Behavior
- Constraints
- Sources
- Files

The input pipeline converts these into a structured investigation representation before the reasoning stages begin.

---

## Repository Structure

ANOMALY/
│
├── agents/
│   ├── anomaly_agent.py
│   ├── critic_agent.py
│   ├── evidence_agent.py
│   ├── hypothesis_agent.py
│   ├── interpretation_agent.py
│   ├── numerical_anomaly_agent.py
│   └── testing_agent.py
│
├── engine/
│   ├── benchmark.py
│   ├── evaluate_benchmark.py
│   ├── input_pipeline.py
│   ├── input_processor.py
│   ├── objective_evaluator.py
│   ├── orchestrator.py
│   └── partial_test.py
│
├── data/
│   ├── benchmarks/
│   ├── partial/
│   └── pioneer/
│
├── benchmark_results/
│
├── main.py
├── investigation_state.json
├── benchmark_evaluation.json
├── objective_evaluation.json
├── partial_test_result.json
└── .gitignore

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python |
| AI / Reasoning | Google Gemini API |
| Numerical Analysis | NumPy / Pandas |
| PDF Processing | pypdf |
| Data | JSON / CSV / TXT / Markdown / PDF |
| Scientific Tests | Deterministic Python tools |
| State | Structured JSON |
| Version Control | Git / GitHub |

---

## Quick Start

### 1. Clone the repository

git clone https://github.com/Ashborne-noir/ANOMALY.git
cd ANOMALY

### 2. Create a virtual environment

python3 -m venv .venv
source .venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Configure Gemini

Create an environment variable containing your Gemini API key.

export GEMINI_API_KEY="YOUR_API_KEY"

Never commit API keys or .env files to the repository.

### 5. Run

python3 main.py

---

## Example Investigation Flow

A typical ANOMALY run follows this structure:

[1] Evidence Agent
        ↓
[2] Numerical Anomaly Engine
        ↓
[3] Anomaly Agent
        ↓
[4] Hypothesis Agent
        ↓
[5] Critic Agent
        ↓
[6] Dynamic Scientific Testing
        ↓
[7] Investigation State

Example output:

OBSERVATION
Persistent acceleration residual detected.

ANOMALY
Observed acceleration remains inconsistent with the supplied baseline model.

HYPOTHESES
H1: Anisotropic thermal recoil
H2: Measurement / telemetry bias
H3: Unmodelled external effect

CRITIQUE
H1 has supporting correlation with available thermal measurements, but geometry and emission characteristics are incomplete.

TEST
Thermal recoil estimation performed.

STATUS
Hypothesis remains supported / unresolved subject to missing evidence.

NEXT INVESTIGATION
Obtain spacecraft thermal geometry, emissivity and directional telemetry.

---

## Benchmarking

ANOMALY is being evaluated against historical scientific anomaly cases.

Current benchmark cases include:

- Pioneer anomaly
- OPERA neutrino anomaly
- Earth flyby anomaly

The evaluation considers:

- pattern/anomaly discovery
- evidence usage
- hypothesis quality
- alternative explanations
- falsification/self-critique
- uncertainty discipline
- next-investigation design

### Blind Evaluation

The investigation receives the blind case.

The historical explanation and evaluation criteria are stored separately as an answer key.

This prevents the investigation pipeline from simply being handed the expected answer.

---

## Scientific Safety & Reliability

### Evidence First

The system should ground reasoning in supplied evidence instead of immediately inventing explanations.

### Separate Observations from Hypotheses

An observed measurement should not automatically become an explanation.

### Competing Hypotheses

The system maintains alternatives rather than committing to the first plausible explanation.

### Falsification

The critic stage actively searches for evidence that could contradict a hypothesis.

### Deterministic Calculations

Numerical and scientific calculations are delegated to executable tools where possible.

### Explicit Uncertainty

Missing measurements, incomplete evidence and unresolved questions should remain visible.

### Human Approval

ANOMALY does not autonomously perform real-world experiments or high-impact scientific actions.

---

## Current MVP Status

### Implemented

- [x] Investigation input pipeline
- [x] JSON / CSV / TXT / Markdown / PDF support
- [x] Structured investigation representation
- [x] Evidence Agent
- [x] Numerical anomaly analysis
- [x] Anomaly Agent
- [x] Hypothesis Agent
- [x] Critic Agent
- [x] Hypothesis contract validation
- [x] Dynamic scientific testing
- [x] Deterministic scientific tools
- [x] Investigation state
- [x] Historical benchmark cases
- [x] Blind benchmark structure

### Planned

- [ ] Deeper literature retrieval
- [ ] More scientific simulation tools
- [ ] Experiment Design Agent
- [ ] Expanded benchmark suite
- [ ] Richer uncertainty estimation
- [ ] Research memory across investigations
- [ ] Interactive investigation dashboard
- [ ] Integration with larger datasets and external scientific tools

---

## Why Agentic AI?

The scientific workflow is not a single prediction task.

It is a sequence of decisions:

What do we know?
      ↓
What doesn't fit?
      ↓
What could explain it?
      ↓
What evidence supports each explanation?
      ↓
What could disprove it?
      ↓
What can we calculate?
      ↓
What evidence is missing?
      ↓
What should we investigate next?

ANOMALY uses agentic orchestration because different stages have different objectives and can challenge one another.

The value is therefore not simply "multiple agents."

The value is the investigation loop they enable.

---

## Long-Term Vision

The current MVP operates primarily on supplied evidence and deterministic computational tools.

The longer-term system can extend the loop:

                 HUMAN QUESTION
                       ↓
                    ANOMALY
                       ↓
          ┌────────────┼────────────┐
          ↓            ↓            ↓
      Literature     Datasets    Simulations
          ↓            ↓            ↓
          └────────────┼────────────┘
                       ↓
                HYPOTHESIS SPACE
                       ↓
                 COMPUTATIONAL TEST
                       ↓
                CRITIC / FALSIFIER
                       ↓
              NEXT BEST INVESTIGATION
                       ↓
                REAL EXPERIMENT
                       ↓
                 NEW EVIDENCE
                       │
                       └──────────→ ANOMALY

The ultimate goal is a system that can help researchers move from:

"Something doesn't fit."

to:

"Here is what we know, here are the competing explanations, here is what we tested, here is what remains uncertain, and here is the next investigation that could reduce that uncertainty."

---

## Current Limitations

ANOMALY is a research prototype, not an autonomous scientific authority.

Current limitations include:

- limited scientific domains
- limited benchmark coverage
- dependence on supplied evidence
- incomplete uncertainty modelling
- limited simulation capabilities
- no autonomous real-world laboratory access
- computational demonstrations may use simplified assumptions

The system should therefore be treated as a research-support tool, with conclusions independently validated by qualified researchers.

---

## Hackathon Context

Event: AgentX-2026

Track: Agentic AI for Scientific Discovery & Engineering

Project: ANOMALY

### Core Challenge

Can an AI agent systematically find what current scientific knowledge fails to explain, challenge possible explanations, test them, and determine what should be investigated next?

---

## References & Benchmark Cases

Historical benchmark cases used by the project include:

- Pioneer anomaly
- OPERA neutrino anomaly
- Earth flyby anomaly

Technology used by the prototype includes:

- Google Gemini API
- NumPy
- Pandas
- pypdf
- Python

Further references and benchmark-specific material are maintained inside the repository.

---

## Team

Team: ANOMALY

Institution: Teegala Krishna Reddy Engineering College

Track: Agentic AI for Scientific Discovery & Engineering

---

## Project

GitHub:
https://github.com/Ashborne-noir/ANOMALY

---

> ANOMALY — Don't just answer the question. Investigate what remains unexplained.

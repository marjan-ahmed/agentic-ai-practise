# 🤖 Agentic AI Practice with OpenAI Agents SDK

This repository contains my hands-on practice with the **OpenAI Agents SDK**.  
The goal is to build a strong foundation in agentic AI concepts by experimenting with different features, error handling strategies, and SDK internals.

---

## 📚 Topics Practiced

### 1. General Concepts & Defaults
- Understanding the overall structure of an Agent
- Default behaviors and fallback mechanisms

### 2. Handoffs
- Concept of handoffs between agents/tools
- Usage patterns and key parameters
- Callback functions during handoff

### 3. Tool Calls & Error Handling
- Making tool calls safely
- Handling unexpected tool failures
- Retrying and fallback strategies

### 4. Dynamic Instructions & Context Objects
- Modifying instructions at runtime
- Passing and using `context` objects effectively

### 5. Guardrails
- Purpose of guardrails in agent safety
- When to apply tripwires and input validation
- Timing of guardrail execution

### 6. Tracing
- Difference between **traces** and **spans**
- Tracking multi-run traces for debugging and observability

### 7. Hooks
- Usage of `RunHooks` and `AgentHooks`
- Extending behavior with custom hooks

### 8. Exception Handling
- Handling common exceptions:
  - `MaxTurnsExceeded`
  - `ModelBehaviorError`
  - And more…
- Graceful recovery strategies

### 9. Runner Methods
- Practiced with:
  - `run`
  - `run_sync`
  - `run_streamed`
- Identified the best use cases for each

### 10. Model Settings
- Understanding `ModelSettings`
- Usage of the `resolve()` method for config management

### 11. Output Type & Schema Strictness
- How `output_type` influences responses
- Enforcing schema strictness in agent outputs

---

## 🛠️ Tech Stack
- **Python 3.11+**
- **OpenAI Agents SDK**
- Virtual environment with dependencies listed in `requirements.txt`

---

## 🚀 Getting Started

Clone the repository:
```bash
git clone https://github.com/marjan-ahmed/agentic-ai-practise.git
cd agentic-ai-practise

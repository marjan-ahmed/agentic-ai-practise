import asyncio
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
    function_tool,
    RunConfig,
    MaxTurnsExceeded,
    enable_verbose_stdout_logging,
)

# enable_verbose_stdout_logging()

# ----------------------------
# Mock/simplified model (no API key required)
class MockChatModel:
    def __init__(self):
        pass
    # Add any necessary mock methods here

mock_model = MockChatModel()

# ----------------------------
# Structured output
class SimpleResponse(BaseModel):
    text: str

class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

# ----------------------------
# Guardrail agent
guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking for math homework help. Return is_math_homework (bool) and reasoning (short).",
    output_type=MathHomeworkOutput,
    model=mock_model,
)

@input_guardrail
async def math_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )

# ----------------------------
# Tools
@function_tool
def get_invoice_status(invoice_id: str) -> str:
    invoice_db = {
        "INV-123": "Invoice INV-123: Paid on 2025-01-15 (Transaction #TXN789).",
        "INV-456": "Invoice INV-456: Due on 2025-09-30, amount $120.00.",
    }
    return invoice_db.get(invoice_id.strip().upper(), f"Invoice {invoice_id}: not found")

@function_tool
def add_numbers(a: float, b: float) -> float:
    return float(a) + float(b)

# ----------------------------
# Specialized agents
billing_agent = Agent(
    name="Billing Agent",
    instructions="You specialize in billing. Explain invoices clearly.",
    model=mock_model,
    output_type=SimpleResponse,
)

tech_agent = Agent(
    name="Tech Agent",
    instructions="You handle technical issues, troubleshooting, and product errors.",
    model=mock_model,
    output_type=SimpleResponse,
)

# ----------------------------
# Main support agent
support_agent = Agent(
    name="Support Agent",
    instructions=(
        "Operate across 3–4 turns. First give billing explanation, then technical support, "
        "then another example, finally wrap up. Ask 'Shall I continue?' after each partial reply."
    ),
    model=mock_model,
    input_guardrails=[math_guardrail],
    handoffs=[billing_agent, tech_agent],
    tools=[get_invoice_status, add_numbers],
)

# ----------------------------
# Run the orchestration
async def main():
    try:
        response = await Runner.run(
            starting_agent=support_agent,
            input="Explain billing first, then tech, then another example, then summary.",
            run_config=RunConfig(max_turns=4),
        )

        print("Last agent:", response.last_agent.name if response.last_agent else "None")
        print("Final output:", response.final_output)

        for idx, turn in enumerate(response.run_info.turns):
            print(f"\nTurn {idx+1}:")
            print("Agent:", turn.agent.name)
            print("Input:", turn.input)
            print("Output:", turn.output)
            if turn.tools_used:
                print("Tools used:", [tool.name for tool in turn.tools_used])

    except InputGuardrailTripwireTriggered:
        print("❌ Input Guardrail triggered: math-homework detected. Aborting run.")
    except MaxTurnsExceeded:
        print("⚠️ Max turns exceeded. The run was stopped automatically.")

def start():
    asyncio.run(main())

if __name__ == "__main__":
    start()

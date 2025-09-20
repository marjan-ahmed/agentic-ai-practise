import os
import asyncio
from dotenv import load_dotenv
from agents import (
    Agent,
    enable_verbose_stdout_logging,
    GuardrailFunctionOutput,
    output_guardrail,
    Runner,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    RunConfig,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)
from openai import AsyncOpenAI
from pydantic import BaseModel

# ----------------------------
# Load environment variables
load_dotenv()
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

enable_verbose_stdout_logging()
set_tracing_disabled(True)

# ----------------------------
# OpenAI / Gemini client setup
client: AsyncOpenAI = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(GEMINI_MODEL, client)

# ----------------------------
# Output structure
class SimpleResponse(BaseModel):
    text: str

# ----------------------------
# Agent that generates text
textAgent = Agent(
    name="No 'in' Text Agent",
    instructions="Generate a short text message without using the word 'in'.",
    model=model,
    output_type=SimpleResponse
)

# ----------------------------
# Output guardrail
@output_guardrail
async def no_in_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    output: SimpleResponse
) -> GuardrailFunctionOutput:
    # Directly check the output
    result = await Runner.run(textAgent, "hello, Write a short sentence about Karachi without using 'in'.")
    tripwire_triggered = "in" in output.text.lower()

    return GuardrailFunctionOutput(
        output_info=result.final_output,  # keep the same output
        tripwire_triggered=tripwire_triggered
    )

# ----------------------------
# Main agent using the output guardrail
agent = Agent(
    name="No 'in' Agent",
    instructions="Generate text without using 'in'.",
    model=model,
    output_guardrails=[no_in_guardrail],
    output_type=SimpleResponse
)

# ----------------------------
# Run example
async def main():
    try:
        result = await Runner.run(agent, "Write a short sentence about Karachi without using 'in'.", run_config=RunConfig(tracing_disabled=True))
        print("✅ Passed: Output is valid")
        print("Output:", result.final_output.text)
    except OutputGuardrailTripwireTriggered:
        print("❌ Guardrail triggered: Output contains 'in'!")

# ----------------------------
def start():
    asyncio.run(main())

# Run
if __name__ == "__main__":
    start()

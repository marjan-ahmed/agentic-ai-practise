import os
import asyncio
from dotenv import load_dotenv
from agents import (
    Agent,
    enable_verbose_stdout_logging,
    InputGuardrailTripwireTriggered,
    GuardrailFunctionOutput,
    TResponseInputItem,
    input_guardrail,
    Runner,
    RunContextWrapper,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)
from openai import AsyncOpenAI
from pydantic import BaseModel
from pydantic.dataclasses import dataclass

# ----------------------------
# Load environment variables
load_dotenv()
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")
enable_verbose_stdout_logging()
# Disable tracing for cleaner output
set_tracing_disabled(True)

# OpenAI / Gemini client setup
client: AsyncOpenAI = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(GEMINI_MODEL, client)

# ----------------------------

@dataclass
class ScholarshipRequiredCriteria(): # or we can also use BaseModel of pydantic
    age: int
    gpa: float
    recommendation_letter: bool

studentScholarshipRecord = Agent(
    name="scholarship record checker",
    instructions=(
        "Extract the student's age, GPA, and whether they have a recommendation letter. "
        "Constraints: age must be <= 25, GPA must be > 3.5 and <= 4, and they must "
        "have a recommendation letter."
    ),
    model=model,
    output_type=ScholarshipRequiredCriteria
)

# result = Runner.run_sync(starting_agent=studentScholarshipRecord, input="my gpa is 4 and my agae is 22 and have a recommendation letter")
# print(result.final_output)


@input_guardrail
async def scholarship_record_analyzer(
    ctx: RunContextWrapper,
    agent: Agent,
    input: str | list[TResponseInputItem]
):
    result = await Runner.run(
        starting_agent=studentScholarshipRecord,
        input=input,
        context=ctx.context
    )

    condition = (
        result.final_output.age > 25
        or result.final_output.gpa < 3.5
        or not result.final_output.recommendation_letter
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=condition
    )

agent = Agent(
    name="Scholarship Record Analyzer",
    instructions="Check if a student is eligible for a scholarship.",
    input_guardrails=[scholarship_record_analyzer],
    model=model
)

async def main():
    try:
        result = await Runner.run(
            agent,
            "Hi, I am 22 years old, I have 5 GPA and I have a recommendation letter."
        )
        print("✅ Passed (eligible)")
        print(result.input_guardrail_results)
    except InputGuardrailTripwireTriggered:
        print("❌ You are not eligible.")

def start():
    asyncio.run(main())
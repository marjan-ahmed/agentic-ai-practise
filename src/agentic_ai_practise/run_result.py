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

# enable_verbose_stdout_logging()
set_tracing_disabled(True)

# ----------------------------
# OpenAI / Gemini client setup
client: AsyncOpenAI = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(GEMINI_MODEL, client)


# ----------------------------------------------------------

class mybase(BaseModel):
    name:str

agent: Agent = Agent(
    name="Helpful Assistant",
    instructions="Help user with their queries.",
    model=model
)

output = Runner.run_sync(
    starting_agent=agent,
    input="Hi, how are you?"
)

def start():
    pass

    # --------- Run Result attributes ---------
    
    # print(output.raw_responses)
    # print(output.last_agent, "\n")
    # print(output.last_response_id) # None
    # print(output._last_agent)
    # print(output.context_wrapper)
    # print(output.final_output_as(cls=mybase))    
    # print(output.final_output)
    
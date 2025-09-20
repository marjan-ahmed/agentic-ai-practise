import os
import asyncio
from dotenv import load_dotenv
import pprint
from agents import (
    Agent,
    enable_verbose_stdout_logging,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    Runner,
)
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent

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

# ------------------------------------------------------------

agent = Agent(
    name = "helpful assistant",
    instructions="you have to answer all the questions",
    model=model
)

async def main():
    response = Runner.run_streamed(starting_agent=agent, input="tell me the about ai in 8 haiku")
    # print(response)
    # print(response.final_output) # None
    print(response.current_agent, "\n")
    print(response.current_turn)
    
    async for event in response.stream_events():
        # pprint.pprint(event)
        # pprint.pprint(event.data) # raw reponse event
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="",flush=True)
            if "is" in event.data.delta: 
                response.cancel() # using cancel() method to stop streaming
            


def start():
    asyncio.run(main())
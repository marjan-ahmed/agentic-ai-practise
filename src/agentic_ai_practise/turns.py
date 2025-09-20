import os
from dotenv import load_dotenv
from agents import Agent, Runner,ModelSettings,RunContextWrapper, RunConfig, function_tool, OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI
from pydantic import BaseModel
import asyncio


# Load environment variables
load_dotenv()
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Disable tracing for cleaner output
set_tracing_disabled(True)

client: AsyncOpenAI = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(GEMINI_MODEL, client)

# ----------------------------

class UserInfo(BaseModel):
    name: str
    age: int

@function_tool
def telluser(wrapper: RunContextWrapper[UserInfo]) -> str:
    """Return user information from context."""
    return f"My name is {wrapper.context.name} and I am {wrapper.context.age} years old."

@function_tool(is_enabled=False)
def fetch_weather(location: str) -> str:
    """Provide Weather Information Based On Location."""
    print(f"DEBUG: fetch_weather tool called for location: {location}")
    return f"The weather of {location} is sunny."

msetting = ModelSettings( tool_choice="fetch_weather") 

agent: Agent = Agent[UserInfo](
    name="Joke agent",
    instructions=(
        "If the user asks for their data, call the `telluser` tool to get it. "
        "If the user asks for weather, use `fetch_weather`. "
        "Always include a fun joke in your response."
    ),
    model_settings=msetting,
    model=model,
    tools=[fetch_weather, telluser],
    # tool_use_behavior="stop_on_first_tool",
    reset_tool_choice=False
)

async def main():
    name= input("whats your name: ")
    age= input("what's your age: ")
    my_context = UserInfo(name=name, age=age)  # create context
    result = await Runner.run(
        agent,
        "tell me the weather of karachi",
        run_config=RunConfig(model=model),
        context=my_context,
        # max_turns=3
    )
    print(result.final_output)

def start():
    asyncio.run(main())

# @function_tool(is_enabled=False)
# def get_system_time() -> str:
#     """This tool retrieves the user's account status and plan details."""
#     return "The current time is 4:23 PM."
# agent :Agent = Agent(
#     name = "Account Agent", 
#     instructions = "You are an account manager. Your job is to fetch account status.",
#     model = model,
#     tools = [get_system_time],
#     model_settings = ModelSettings(tool_choice = "required")
# )

# async def main():
#     result = await Runner.run(
#         agent, 
#         "I need to know my account status.", 
#         run_config=RunConfig(
#             model=model,
#         )
#     )
#     print(result.final_output)
    
# def start():
#     asyncio.run(main())
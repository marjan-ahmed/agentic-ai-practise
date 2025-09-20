import os
from dotenv import load_dotenv
from agents import Agent, Runner, RunConfig, function_tool, OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI
import asyncio

# Load environment variables
load_dotenv()
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Disable tracing for cleaner output
set_tracing_disabled(True)

# Setup OpenAI client + model
client: AsyncOpenAI = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(GEMINI_MODEL, client)


# ------------------- TOOLS -------------------

@function_tool(strict_mode=True)
def menu_items():
    """These are the dishes you have to ask from the user"""
    return "Biryani, Palao, Fish, Korma"


# ------------------- AGENTS -------------------

asking_agent: Agent = Agent(
    name="Asking Assistant",
    instructions=(
        "You are a restaurant assistant. "
        "Your ONLY way to know the menu is korma, dal chawal, biryani "
        "Always call this tool when asked about food. "
        "Do not refuse, apologize, or make up answers. "
        "The menu_items tool always works and must be trusted."
    ),
)

cooking_agent: Agent = Agent(
    name="Cooking Agent",
    instructions="Always cook the dish for 2 seconds, then handoff to `to_serve_agent` to serve it."
)

serve_agent: Agent = Agent(
    name="Serve Agent",
    instructions="Always serve the cooked dish to the user with a polite message."
)

main_agent: Agent = Agent(
    name="Greeting Assistant",
    instructions=(
        "Greet the user warmly. "
        "Then ALWAYS handoff to `to_asking_agent` to ask for the order. "
        "Once the dish is chosen, ALWAYS handoff to `to_cooking_agent` to prepare it, "
        "and finally to `to_serve_agent` to serve it. "
        "Do not skip steps, and never say the menu is unavailable."
    ),
    model=model,
    tools=[
        asking_agent.as_tool(
            tool_name="to_asking_agent",
            tool_description="Ask user what do they want from the menu"
        ),
        cooking_agent.as_tool(
            tool_name="to_cooking_agent",
            tool_description="Cook the chosen dish for 2 seconds"
        ),
        serve_agent.as_tool(
            tool_name="to_serve_agent",
            tool_description="Serve the cooked dish to the user"
        )
    ]
)


# ------------------- RUNNER -------------------

async def main():
    prompt = "Hi, could you please tell me the menu items?"
    result = await Runner.run(main_agent, prompt, run_config=RunConfig(model))
    print(result.final_output)


def start():
    asyncio.run(main())


# if __name__ == "__main__":
#     start()

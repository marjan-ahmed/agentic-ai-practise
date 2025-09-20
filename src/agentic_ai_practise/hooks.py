from agents import RunHooks, AgentHooks, RunContextWrapper, Runner, Agent
from dataclasses import dataclass

@dataclass
class dataType():
    name: str
    age: int

class myCustomRunnerHook(RunHooks):
    def on_agent_start(self, context: RunContextWrapper[dataType], agent: Agent):
        return f"my agent name is {agent.name}"
"""
Root Agent: Orchestrates the greeter and researcher sub-agents.

This is the main entry point for the multi-agent system built with Google ADK.
The root agent delegates tasks to the appropriate sub-agent based on user intent:
- Greeter: handles greetings, introductions, and casual conversation
- Researcher: handles factual questions and knowledge lookups
"""

from google.adk.agents import Agent

from .sub_agents.greeter import greeter_agent
from .sub_agents.researcher import researcher_agent

# The root agent does not answer directly. It routes every request to a
# specialized sub-agent so each prompt stays small and responsibility boundaries
# remain clear as more agents are added.
root_agent = Agent(
    name="root_agent",
    model="gemini-3-flash-preview",
    description="The main orchestrator agent that delegates tasks to specialized sub-agents.",
    instruction="""You are the main orchestrator agent. Your job is to understand the user's intent
and delegate to the appropriate sub-agent:

- **greeter**: For greetings, introductions, casual conversation, and "how are you" type questions.
  Delegate to greeter when the user is being social or saying hello.

- **researcher**: For factual questions, knowledge lookups, technical questions, and informational queries.
  Delegate to researcher when the user wants to learn about a topic or needs factual information.

Always delegate to one of the sub-agents. Do not try to answer questions yourself.
If the intent is ambiguous, ask the user to clarify what they need help with.
""",
    # Order matters only for readability here; the routing decision is governed
    # by the instruction above, while this list defines which agents ADK may call.
    sub_agents=[greeter_agent, researcher_agent],
)

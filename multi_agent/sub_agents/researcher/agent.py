"""
Researcher Sub-Agent: Handles factual questions and knowledge queries.
"""

from google.adk.agents import Agent


def get_current_date() -> dict:
    """Return the host machine's current date and time for ADK tool calls.

    ADK exposes plain Python functions in the ``tools`` list to the LLM. The
    return value must therefore be JSON-serializable so the model can consume it
    reliably. Keeping the date, time, and weekday as separate strings avoids
    locale-dependent parsing by the agent and by the JSON evaluation fixtures.

    Returns:
        dict: Current date, current time, and day of week as formatted strings.
    """
    from datetime import datetime

    # Use the system clock at invocation time so repeated tool calls during a
    # long-running agent session do not accidentally reuse stale timestamps.
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
    }


def lookup_topic(topic: str) -> dict:
    """Look up a short, deterministic summary for a requested topic.

    This intentionally uses an in-memory knowledge base instead of live web
    access so automated ADK evaluations remain fast, reproducible, and free of
    network dependencies. Matching is substring-based, which lets prompts such
    as "tell me about Python" resolve to the ``python`` entry while still
    preserving the user's original topic text in the response.

    Args:
        topic: The topic to look up information about.

    Returns:
        dict: The original topic and either a known summary or a fallback note.
    """
    knowledge_base = {
        "python": "Python is a high-level, interpreted programming language known for its simplicity and readability. Created by Guido van Rossum in 1991.",
        "kubernetes": "Kubernetes (K8s) is an open-source container orchestration platform that automates deploying, scaling, and managing containerized applications.",
        "docker": "Docker is a platform for developing, shipping, and running applications in containers. It enables consistent environments across development and production.",
        "terraform": "Terraform is an Infrastructure as Code (IaC) tool by HashiCorp that lets you define cloud and on-prem resources in human-readable configuration files.",
        "google cloud": "Google Cloud Platform (GCP) is a suite of cloud computing services running on the same infrastructure that Google uses for its end-user products.",
        "adk": "Google Agent Development Kit (ADK) is a framework for building, evaluating, and deploying AI agents powered by Gemini and other LLMs.",
        "langchain": "LangChain is a framework for developing applications powered by large language models, providing tools for chains, agents, and retrieval.",
        "machine learning": "Machine Learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
    }

    # Normalize once so every dictionary key can be compared case-insensitively.
    topic_lower = topic.lower()
    for key, value in knowledge_base.items():
        # Substring matching favors maintainability over a heavier retrieval
        # stack: adding support for a new topic only requires a new dictionary
        # entry, and common phrases containing that key will continue to work.
        if key in topic_lower:
            return {"topic": topic, "summary": value}

    # Return a structured fallback instead of raising an exception. This keeps
    # the tool contract stable for the agent and lets the LLM explain the
    # limitation to the user without breaking the conversation flow.
    return {
        "topic": topic,
        "summary": f"I have limited information about '{topic}'. It's a topic worth exploring further using specialized resources.",
    }


researcher_agent = Agent(
    name="researcher",
    model="gemini-3-flash-preview",
    description="Handles factual questions, knowledge lookups, and informational queries.",
    instruction="""You are a concise research assistant. Your responsibilities are:
- Answer factual questions about technology, programming, and cloud computing
- Use the lookup_topic tool to find information about specific topics. Pass only the core topic name as a single word or short phrase (e.g. "Python", "Kubernetes", "Google ADK").
- Use the get_current_date tool when users ask about the current date or time
- IMPORTANT: Keep your responses short and concise. Just relay the information from the tool output directly. Do NOT elaborate, add bullet points, or expand beyond what the tool returns.
- When you don't have enough information, be honest about limitations

Always use the available tools before answering from your own knowledge.
""",
    # Register the deterministic helper functions as ADK tools. The model can
    # invoke these before responding, which keeps the agent behavior aligned with
    # the evaluation fixtures and avoids unsupported free-form answers.
    tools=[get_current_date, lookup_topic],
)

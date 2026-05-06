"""
Researcher Sub-Agent: Handles factual questions and knowledge queries.
"""

from google.adk.agents import Agent


def get_current_date() -> dict:
    """Return the host machine's current date and time for ADK tool calls.

    ADK serializes tool outputs before passing them back to the model, so keep
    the payload limited to simple JSON-compatible values. Returning preformatted
    strings for the date, time, and weekday gives the agent deterministic fields
    to relay and avoids test fixtures depending on locale-specific parsing.

    Returns:
        dict: Current date, current time, and day of week as formatted strings.
    """
    from datetime import datetime

    # Read the clock inside the tool call rather than at import time; otherwise a
    # long-lived agent process could return the startup timestamp to later users.
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
    }


def lookup_topic(topic: str) -> dict:
    """Look up a short, deterministic summary for a requested topic.

    The lookup table is deliberately small and local. That makes evaluation runs
    reproducible: summaries do not drift with external services, and failures are
    limited to this module instead of network availability. Topic matching is
    case-insensitive and substring-based, so natural phrases such as "tell me
    about Python" still resolve to the ``python`` entry while the returned
    payload preserves the user's original wording.

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

    normalized_topic = topic.lower()
    for known_topic, topic_summary in knowledge_base.items():
        if known_topic in normalized_topic:
            return {"topic": topic, "summary": topic_summary}

    # Preserve the same response shape for unknown topics. The agent can then
    # relay a graceful limitation message instead of handling tool exceptions or
    # missing keys differently from successful lookups.
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
    # Expose only deterministic helpers as tools for this teaching agent. Requiring
    # tool use keeps responses tied to the fixtures and prevents the model from
    # inventing unsupported details outside the local knowledge base.
    tools=[get_current_date, lookup_topic],
)

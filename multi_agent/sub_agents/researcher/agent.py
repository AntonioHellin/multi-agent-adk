"""
Researcher Sub-Agent: Handles factual questions and knowledge queries.
"""

from google.adk.agents import Agent


def get_current_date() -> dict:
    """Get the current date and time.

    Returns:
        dict: A dictionary containing the current date and time in ISO format.
    """
    from datetime import datetime

    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
    }


def lookup_topic(topic: str) -> dict:
    """Look up information about a given topic. Returns a brief summary.

    Args:
        topic: The topic to look up information about.

    Returns:
        dict: A dictionary containing the topic and a brief summary about it.
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
    tools=[get_current_date, lookup_topic],
)

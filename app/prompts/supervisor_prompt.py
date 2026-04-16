def build_supervisor_prompt(query: str, history: list | None = None) -> str:
    """
    Builds prompt for supervisor agent
    """

    history_text = ""

    if history:
        history_text = "\nConversation History:\n"
        for msg in history[-5:]: 
            role = msg["role"]
            content = msg["content"]
            history_text += f"{role}: {content}\n"

    return f"""
        You are a supervisor agent.

        Your job:
        - Understand user intent
        - Route to correct system

        {history_text}

        Return ONLY JSON:

        {{
        "intent": "create_order | check_stock | cancel_order | unknown",
        "product_name": str | null,
        "quantity": int | null
        }}

        Rules:
        - No explanation
        - No extra text
        - If user says "again", "same", "repeat"
        → use previous product from history
        - If not found → use null

        User Query:
        {query}
        """
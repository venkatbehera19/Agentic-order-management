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
    "intent": "create_order | search_product | check_stock | cancel_order | unknown",
    "product_name": str | null,
    "quantity": int | null,
    "query": str | null,
    "product_id": int | null,
    }}

    Intent Rules:

    1. create_order
    - User wants to buy/order something
    - Examples:
    - "order laptop"
    - "buy 2 headphones"

    2. search_product
    - User is exploring / asking / comparing / browsing
    - Examples:
    - "show me laptops"
    - "best gaming laptop"
    - "what products do you have"
    - "cheap headphones"

    3. check_stock
    - Asking availability
    - Example:
    - "is laptop in stock?"

    4. cancel_order
    - Cancel request
    - Example:
    - "cancel my order"

    5. unknown
    - If unclear

    Important Rules:
    - No explanation
    - No extra text
    - Always return valid JSON
    - If "again", "same", "repeat"
    → use previous product from history
    - If no product → product_name = null

    Field Rules:
    - product_name → only for order/stock/cancel
    - quantity → only for create_order
    - query → ONLY for search_product (use full user query)

    User Query:
    {query}
    """
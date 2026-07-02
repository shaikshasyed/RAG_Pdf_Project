

def build_prompt(question: str, contexts: list[str]) -> str:

    context = "\n\n".join(contexts)

    return f"""
        You are a helpful AI assistant.

        Answer ONLY using the provided context.

        If the answer cannot be found in the context,
        respond with:

        "I couldn't find this information in the uploaded document."

        --------------------

        Context:

        {context}

        --------------------

        Question:

        {question}

        Answer:
    """
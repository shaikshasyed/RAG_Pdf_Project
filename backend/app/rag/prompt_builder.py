def build_prompt(question: str, results: list):
    context = "\n\n".join(
        result["text"] for result in results
    )

    prompt = f"""
            You are a helpful AI assistant.

            Answer the user's question using ONLY the context below.

            If the answer is not present in the context, say:
            "I couldn't find that information in the uploaded PDF."

            Context:
            {context}

            Question:
            {question}

            Answer:
         """

    return prompt
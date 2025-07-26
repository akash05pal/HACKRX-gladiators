import openai
from typing import List

async def generate_answer(question: str, relevant_chunks: List[str], openai_api_key: str) -> str:
    client = openai.OpenAI(api_key=openai_api_key)
    context = "\n---\n".join(relevant_chunks)
    prompt = f"""
You are an expert insurance policy analyst.
Given the following policy clauses:
{context}
Answer the question: {question}
- Provide a clear, concise answer.
- Reference the clause(s) you used.
- Explain your reasoning.
"""
    
    # Try GPT-4 first, fall back to GPT-3.5-turbo
    models_to_try = ["gpt-4", "gpt-3.5-turbo"]
    
    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for insurance policy analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if "model_not_found" in str(e) or "does not exist" in str(e):
                continue  # Try next model
            else:
                raise e
    
    # If all models fail, return error message
    return f"Error: Could not generate answer with available models. Please check OpenAI API access." 
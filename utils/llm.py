import openai
from typing import List

def generate_answer(question: str, relevant_chunks: List[str], openai_api_key: str) -> str:
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
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for insurance policy analysis."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.2
    )
    return response.choices[0].message.content.strip() 
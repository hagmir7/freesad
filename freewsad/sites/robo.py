import os
from openai import OpenAI


def bot(prompt):
    try:
        client = OpenAI(api_key=str(os.environ.get("AI_KEY")))
        stream = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                return chunk.choices[0].delta.content

    except Exception as e:
        print("Error")
        return str(e)

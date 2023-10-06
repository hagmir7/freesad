import openai
import os



openai.api_key = os.environ.get('AI_KEY')

def bot(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=4000,  # Adjust the max tokens as needed
            n=1,
            stop=None,
            temperature=0.7  # Adjust the temperature for randomness
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return str(e)



import openai



# Set your OpenAI API key
api_key = "YOUR_API_KEY_HERE"
openai.api_key = "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"

def bot(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=400,  # Adjust the max tokens as needed
            n=1,
            stop=None,
            temperature=0.7  # Adjust the temperature for randomness
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return str(e)



from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

completion = client.chat.completions.create(
  extra_body={},
  model="thudm/glm-z1-32b:free",
  messages=[
    {
      "role": "user",
      "content": "Hello. How are you?"
    }
  ]
)
print(completion.choices[0].message.content)
import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# Load environment variables from .env file
load_dotenv()

# Create an OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        # Handle errors gracefully
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    messages = [{"role": "system", "content": "You are ChatGPT, a helpful assistant."}]
    print("Welcome to the ChatGPT assistant. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Assistant: Goodbye!")
            break
        messages.append({"role": "user", "content": user_input})
        response = get_response(messages)
        if response:
            print(f"Assistant: {response}\n")
            messages.append({"role": "assistant", "content": response})

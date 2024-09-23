import tkinter as tk
from tkinter import scrolledtext
import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# Load environment variables from .env file
load_dotenv()

# Create an OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize conversation messages
messages = [{"role": "system", "content": "You are ChatGPT, a helpful assistant."}]

def get_response(event=None):
    user_input = user_entry.get()
    if user_input.strip() == '':
        return
    user_entry.delete(0, tk.END)
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, "You: " + user_input + '\n')
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)  # Auto-scroll to the bottom
    messages.append({"role": "user", "content": user_input})
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        assistant_response = response.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": assistant_response})
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, "Assistant: " + assistant_response + '\n')
        chat_area.config(state=tk.DISABLED)
        chat_area.yview(tk.END)  # Auto-scroll to the bottom
    except OpenAIError as e:
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, f"An error occurred: {e}\n")
        chat_area.config(state=tk.DISABLED)
        chat_area.yview(tk.END)

# Create the main window
root = tk.Tk()
root.title("ChatGPT Assistant")

# Configure window size
root.geometry("600x500")

# Create a text area for the chat history
chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED)
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create an entry widget for user input
user_entry = tk.Entry(root)
user_entry.pack(padx=10, pady=5, fill=tk.X)
user_entry.bind("<Return>", get_response)

# Create a send button
send_button = tk.Button(root, text="Send", command=get_response)
send_button.pack(padx=10, pady=5)

root.mainloop()

import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import os
import json
from dotenv import load_dotenv
import openai
from openai import OpenAIError
import datetime
import threading

# Load environment variables from .env file
load_dotenv()

# Set up the OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# File to store chats
CHAT_HISTORY_FILE = "chats.json"

# Initialize chats dictionary
# Each chat is a list of messages
chats = {}
chat_names = {}  # Mapping from chat_id to display name
current_chat_id = None  # This will store the current chat ID


# Fetch available models that are chat models
def get_available_models():
    try:
        models = client.models.list()
        # Filter models that are chat models
        chat_models = [model.id for model in models if 'gpt' in model.id]
        return sorted(set(chat_models))
    except OpenAIError as e:
        print(f"Error fetching models: {e}")
        # Fallback models if fetching fails
        return ["gpt-3.5-turbo", "gpt-4"]


available_models = get_available_models()
current_model = "gpt-4" if "gpt-4" in available_models else available_models[0]


def save_chats():
    with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump({'chats': chats, 'chat_names': chat_names}, f, ensure_ascii=False, indent=4)


def load_chats():
    global chats, chat_names
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            chats = data.get('chats', {})
            chat_names = data.get('chat_names', {})


def update_chat_listbox():
    chat_listbox.delete(0, tk.END)
    for chat_id, name in chat_names.items():
        chat_listbox.insert(tk.END, name)


def get_response(event=None):
    global chats, current_chat_id, current_model, chat_names
    user_input = user_entry.get()
    if user_input.strip() == '':
        return
    user_entry.delete(0, tk.END)
    chat_area.config(state=tk.NORMAL)
    # Insert a space before user message
    chat_area.insert(tk.END, '\n')
    # Display user message with formatting
    chat_area.insert(tk.END, "You: ", 'bold')
    chat_area.insert(tk.END, user_input + '\n', 'user_bg')
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)  # Auto-scroll to the bottom

    # Append user message to current chat
    chats[current_chat_id].append({"role": "user", "content": user_input})

    # If this is the first user message, generate chat name
    if len(chats[current_chat_id]) == 2:  # 1 system message + 1 user message
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        chat_name = f"{user_input[:20]}... ({timestamp})"
        chat_names[current_chat_id] = chat_name
        update_chat_listbox()
        save_chats()

    # Start a new thread to handle the streaming response
    threading.Thread(target=stream_response, daemon=True).start()


def stream_response():
    global chats, current_chat_id, current_model
    try:
        stream = client.chat.completions.create(
            model=current_model,
            messages=[{"role": msg["role"], "content": msg["content"]} for msg in chats[current_chat_id]],
            max_tokens=1000,
            temperature=0.7,
            stream=True
        )

        assistant_response = ''
        # Schedule insertion of assistant label
        chat_area.after(0, insert_assistant_label)

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                assistant_response += content
                # Schedule insertion of content
                chat_area.after(0, insert_assistant_content, content)

        # Append the assistant's response to the chat history
        chats[current_chat_id].append({"role": "assistant", "content": assistant_response})
        save_chats()
    except OpenAIError as e:
        # Handle API errors
        chat_area.after(0, insert_error_message, f"API Error: {e}")
    except Exception as e:
        # Handle other errors
        chat_area.after(0, insert_error_message, f"Unexpected Error: {e}")


def insert_assistant_label():
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, '\n')
    chat_area.insert(tk.END, "Assistant: ", 'bold')
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)


def insert_assistant_content(content):
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, content)
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)


def insert_error_message(error_message):
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"\nAn error occurred: {error_message}\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)


def new_chat():
    global chats, current_chat_id, chat_names
    # Generate a new chat ID using timestamp and unique identifier
    chat_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    chats[chat_id] = [{"role": "system", "content": "You are ChatGPT, a helpful assistant."}]
    chat_names[chat_id] = "New Chat"
    current_chat_id = chat_id
    # Add chat to sidebar
    update_chat_listbox()
    chat_listbox.selection_clear(0, tk.END)
    chat_listbox.selection_set(tk.END)
    # Clear chat area
    chat_area.config(state=tk.NORMAL)
    chat_area.delete(1.0, tk.END)
    chat_area.config(state=tk.DISABLED)
    save_chats()


def on_chat_select(event):
    global chats, current_chat_id
    selection = chat_listbox.curselection()
    if selection:
        index = selection[0]
        chat_id = list(chat_names.keys())[index]
        current_chat_id = chat_id
        # Load messages into chat area
        chat_area.config(state=tk.NORMAL)
        chat_area.delete(1.0, tk.END)
        for message in chats[current_chat_id]:
            role = message['role']
            content = message['content']
            # Insert a space before message
            chat_area.insert(tk.END, '\n')
            if role == 'user':
                chat_area.insert(tk.END, "You: ", 'bold')
                chat_area.insert(tk.END, content + '\n', 'user_bg')
            elif role == 'assistant':
                chat_area.insert(tk.END, "Assistant: ", 'bold')
                chat_area.insert(tk.END, content + '\n')
        chat_area.config(state=tk.DISABLED)
        chat_area.yview(tk.END)


def change_model(event):
    global current_model
    current_model = model_var.get()


# Create the main window
root = tk.Tk()
root.title("ChatGPT Assistant")

# Configure window size
root.geometry("800x600")

# Create frames
left_frame = tk.Frame(root, width=200)
left_frame.pack(side=tk.LEFT, fill=tk.Y)

right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Left Frame Widgets
chat_listbox = tk.Listbox(left_frame)
chat_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
chat_listbox.bind('<<ListboxSelect>>', on_chat_select)

new_chat_button = tk.Button(left_frame, text="New Chat", command=new_chat)
new_chat_button.pack(side=tk.TOP, fill=tk.X)

# Dropdown to select model
model_var = tk.StringVar(root)
model_var.set(current_model)
model_dropdown = ttk.Combobox(left_frame, textvariable=model_var, values=available_models)
model_dropdown.bind('<<ComboboxSelected>>', change_model)
model_dropdown.pack(side=tk.TOP, fill=tk.X)

# Right Frame Widgets
# Create a text area for the chat history
chat_area = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, state=tk.DISABLED)
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Define text tags for formatting
chat_area.tag_config('bold', font=('TkDefaultFont', 16, 'bold'))



# Create an entry widget for user input
user_entry = tk.Entry(right_frame)
user_entry.pack(padx=10, pady=5, fill=tk.X)
user_entry.bind("<Return>", get_response)

# Create a send button
send_button = tk.Button(right_frame, text="Send", command=get_response)
send_button.pack(padx=10, pady=5)

# Load existing chats
load_chats()
update_chat_listbox()

# Initialize first chat if none exist
if not chats:
    new_chat()
else:
    # Select the first chat
    chat_listbox.selection_set(0)
    on_chat_select(None)

root.mainloop()
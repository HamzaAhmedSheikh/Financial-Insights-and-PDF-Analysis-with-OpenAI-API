import os
import time
from dotenv import load_dotenv, find_dotenv
import json
import openai
import streamlit as st

from openai.types.beta import Assistant
from openai.types.beta.thread import Thread

def initialize_openai_client(api_key):
    return openai.OpenAI(api_key=api_key)

# Load the API key from the .env file
load_dotenv(find_dotenv())

api_key = os.getenv("OPENAI_API_KEY")

client: openai.OpenAI = openai.OpenAI(api_key = api_key)

assistant: Assistant = client.beta.assistants.create(
    name = "Finance Insight Analyst",
    instructions = "You are a helpful financial analyst expert and, focusing on management discussions and financial results. help people learn about financial needs and guid them towards fincial literacy.",
    tools = [{"type":"code_interpreter"}, {"type": "retrieval"}],
    model = "gpt-3.5-turbo-1106"
)

def show_json(obj):
    print(json.dumps(json.loads(obj.model_dump_json()), indent=4))

show_json(assistant)

# Creating a Thread for Conversation
thread: Thread = client.beta.threads.create()

# Submitting User Message
def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )

    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

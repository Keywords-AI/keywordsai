from dotenv import load_dotenv
load_dotenv("tests/.env", override=True)

import openai
from keywordsai_tracing import KeywordsAITelemetry, workflow, task
from time import sleep
from threading import Thread
from opentelemetry import trace, context as context_api
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)

k_tl = KeywordsAITelemetry()

@task(name="another_generation")
def another_generation(prompt):
    print(f"another_generation - Current span: {trace.get_current_span()}")
    print(f"another_generation - Is recording: {trace.get_current_span().is_recording()}")
    sleep(2)  # Reduced sleep time for faster testing
    return "This is the response of other generation"

@workflow(name="explain_concept")
def explain_concept(topic):
    print(f"explain_concept - Current span: {trace.get_current_span()}")
    print(f"explain_concept - Is recording: {trace.get_current_span().is_recording()}")
    
    prompt = f"Explain {topic}"
    
    # This will NOT work - context is not propagated to new thread
    print("\n=== Testing WITHOUT context propagation ===")
    thread = Thread(target=another_generation, args=(prompt,))
    thread.start()
    thread.join()
    
    # This WILL work - manually propagate context
    print("\n=== Testing WITH context propagation ===")
    current_context = context_api.get_current()
    
    def run_with_context():
        # Attach the context in the new thread
        token = context_api.attach(current_context)
        try:
            another_generation(prompt)
        finally:
            context_api.detach(token)
    
    thread_with_context = Thread(target=run_with_context)
    thread_with_context.start()
    thread_with_context.join()
    
    return "Done testing"

# Test it
print("=== Starting threading context test ===")
result = explain_concept("black holes")
print(f"Result: {result}")

# Flush to ensure all spans are sent
k_tl.flush() 
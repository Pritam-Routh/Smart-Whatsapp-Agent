from agent.agent_v0 import process_messages

if __name__ == "__main__":
    print("🤖 Starting Gemini Assistant...")
    process_messages(messages_path="inputs/messages.json", output_path="output.json")

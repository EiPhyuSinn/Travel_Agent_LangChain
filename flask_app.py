from flask import Flask, render_template, request, jsonify
from langchain.agents import AgentType, initialize_agent
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from custom_tools import AviationstackTool, AviationstackAirportTool
import os

load_dotenv()
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.7
)

tools = [
    AviationstackTool(),
    AviationstackAirportTool()
]

custom_prompt = ChatPromptTemplate.from_template(
    """
You are a helpful assistant. Use the tools available to answer flight and airport queries.

Provide the final answer as a clear, natural language text summary (not JSON).

Question: {input}
"""
)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    prompt=custom_prompt
)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    response = agent.run(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)

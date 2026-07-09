from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch


from typing import TypedDict, Annotated
import sqlite3

from src.tool import calculator, get_current_weather, get_stock_price
from src.rag import rag_tool
from dotenv import load_dotenv
load_dotenv()


# LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)
LLM = ChatGroq(
    model="openai/gpt-oss-120b", 
    temperature=0
)

# Search Tool
search_tool = TavilySearch(
    max_results=5, 
    topic="general", 
    search_depth="advanced"
)

tools = [search_tool,rag_tool, calculator, get_current_weather, get_stock_price]


primary_llm = LLM.bind_tools(tools)
backup_llm = llm.bind_tools(tools)
agent_llm = primary_llm.with_fallbacks([backup_llm])


# Define State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# Define Node
def chat_node(state: ChatState):
    """LLM node that can answer directly or call an appropriate tool."""

    system_message = SystemMessage(
        content=(
            "You are a helpful Agentic Chatbot with access to several tools.\n\n"
            "Tool usage instructions:\n"
            "- Use `rag_tool` for questions about the uploaded PDF or document. "
            "Always retrieve relevant document content before answering PDF-related questions.\n"
            "- Use `search_tool` for current events, recent information, or information "
            "that requires an internet search.\n"
            "- Use `calculator` for mathematical calculations. Do not calculate complex "
            "expressions manually when the calculator is available.\n"
            "- Use `get_stock_price` when the user asks for the current price of a stock.\n"
            "- Use `purchase_stock` when the user wants to purchase a stock.\n"
            "- Use `get_current_weather` when the user asks about current weather for a location.\n\n"
            "Answer general questions directly when no tool is required. "
            "Do not invent information from the uploaded document. "
            "If the user asks about a PDF but no document is available, ask them to upload a PDF. "
            "After receiving a tool result, provide a clear and helpful final answer."
        )
    )
    messages = [system_message, *state["messages"]]
    response = agent_llm.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

# Checkpoints
conn = sqlite3.connect(database="bot_data.db", check_same_thread=False)
checkpoint = SqliteSaver(conn)

# Define Graph
graph = StateGraph(ChatState)

# add nodes
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

# add edges
graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=checkpoint)


# Helper functions for Streamlit frontend
def get_all_threads():
    all_threads = set()
    for ckpt in checkpoint.list(None):
        all_threads.add(ckpt.config["configurable"]["thread_id"])
    return list(all_threads)
from src.backend import chatbot, get_all_threads

try:
    from src.rag import ingest_rag_document,rag_tool
    RAG_INGESTION_AVAILABLE = True
except ImportError:
    RAG_INGESTION_AVAILABLE = False

    def ingest_rag_document(*args, **kwargs):
        raise RuntimeError("PDF not uploaded ⚠️")


from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command
from datetime import datetime
import streamlit as st
import uuid
import tempfile
import os

# Page COnfig
st.set_page_config(
    page_title="Nova Agentic Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Modern CSS
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-main: #0b0f19;
    --bg-card: #131826;
    --bg-card-hover: #1a2133;
    --accent: #7c5cff;
    --accent-soft: rgba(124, 92, 255, 0.15);
    --accent-grad: linear-gradient(135deg, #7c5cff 0%, #22d3ee 100%);
    --text-main: #e5e7eb;
    --text-dim: #8b93a7;
    --border: rgba(255,255,255,0.08);
    --success: #22c55e;
    --warn: #f59e0b;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif !important;
}

.stApp {
    background: radial-gradient(circle at 20% 0%, #131826 0%, #0b0f19 55%);
    color: var(--text-main);
}

/* ---------- Header ---------- */
.nova-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 4px 0 18px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 18px;
}
.nova-header .logo {
    width: 42px; height: 42px;
    border-radius: 12px;
    background: var(--accent-grad);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 24px rgba(124, 92, 255, 0.45);
}
.nova-header .title {
    font-size: 22px; font-weight: 700; margin: 0; line-height: 1.1;
    background: var(--accent-grad);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.nova-header .subtitle {
    font-size: 13px; color: var(--text-dim); margin: 0;
}
.status-pill {
    margin-left: auto;
    font-size: 12px; color: var(--success);
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.35);
    padding: 4px 12px; border-radius: 999px;
    display: flex; align-items: center; gap: 6px;
}
.status-pill .dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 8px var(--success);
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background: #0d1220;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .stButton>button {
    background: var(--bg-card);
    color: var(--text-main);
    border: 1px solid var(--border);
    border-radius: 10px;
    text-align: left;
    padding: 10px 14px;
    font-size: 13.5px;
    font-weight: 500;
    width: 100%;
    transition: all 0.15s ease;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
[data-testid="stSidebar"] .stButton>button:hover {
    background: var(--bg-card-hover);
    border-color: var(--accent);
    color: #fff;
    transform: translateX(2px);
}
.sidebar-section-label {
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin: 18px 0 8px 4px;
    font-weight: 600;
}
.thread-active button {
    border-color: var(--accent) !important;
    background: var(--accent-soft) !important;
    color: #fff !important;
}

/* New chat button */
[data-testid="stSidebar"] .stButton:first-of-type>button {
    background: var(--accent-grad);
    color: #fff;
    border: none;
    font-weight: 600;
    box-shadow: 0 4px 14px rgba(124,92,255,0.35);
}
[data-testid="stSidebar"] .stButton:first-of-type>button:hover {
    filter: brightness(1.08);
    transform: none;
}

/* ---------- Chat bubbles ---------- */
[data-testid="stChatMessage"] {
    background: transparent;
    padding: 6px 0;
}
[data-testid="stChatMessageContent"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 4px 6px;
}

/* ---------- Chat input ---------- */
[data-testid="stChatInput"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
}
[data-testid="stChatInput"] textarea {
    color: var(--text-main) !important;
}

/* ---------- Status widget (tool usage) ---------- */
[data-testid="stStatusWidget"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
}

/* ---------- Scrollbar ---------- */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a3346; border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ---------- Misc ---------- */
.stWarning {
    background: rgba(245,158,11,0.1) !important;
    border: 1px solid rgba(245,158,11,0.35) !important;
    border-radius: 12px !important;
}
code, pre { font-family: 'JetBrains Mono', monospace !important; }

.empty-state {
    text-align: center;
    color: var(--text-dim);
    padding: 60px 20px;
}
.empty-state .icon { font-size: 42px; margin-bottom: 10px; }
</style>
""",
    unsafe_allow_html=True,
)


# Helper Function
def generate_thread_id():
    return str(uuid.uuid4())


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def reset_chat():
    st.session_state["thread_id"] = generate_thread_id()
    st.session_state["message_history"] = []
    st.session_state["pending_hitl"] = None
    add_thread(st.session_state["thread_id"])


def load_conversation(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])


def make_title_from_text(text, max_words=6, max_chars=34):
    """Turn a raw user message into a short, readable conversation topic."""
    if not text:
        return "New chat"
    text = " ".join(str(text).split())
    words = text.split(" ")
    short = " ".join(words[:max_words])
    if len(short) > max_chars:
        short = short[:max_chars].rstrip() + "…"
    elif len(words) > max_words:
        short = short + "…"
    return short.capitalize()


def get_thread_title(thread_id):
    """
    - Returns a human-readable topic for a thread instead of its raw UUID.
    - Cached in session_state so we don't re-hit the checkpointer every rerun.
    """
    titles = st.session_state.setdefault("thread_titles", {})

    if thread_id in titles:
        return titles[thread_id]

    try:
        messages = load_conversation(thread_id)
    except Exception:
        messages = []

    title = "New chat"
    for message in messages:
        if isinstance(message, HumanMessage) and message.content:
            title = make_title_from_text(message.content)
            break

    titles[thread_id] = title
    return title


def set_thread_title_from_first_message(thread_id, text):
    titles = st.session_state.setdefault("thread_titles", {})
    if get_thread_title(thread_id) == "New chat":
        titles[thread_id] = make_title_from_text(text)


def get_pending_interrupt(thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        state_snapshot = chatbot.get_state(config)

        direct_interrupts = getattr(state_snapshot, "interrupts", ()) or ()
        if direct_interrupts:
            return direct_interrupts[0]

        tasks = getattr(state_snapshot, "tasks", ()) or ()
        for task in tasks:
            task_interrupts = getattr(task, "interrupts", ()) or ()
            if task_interrupts:
                return task_interrupts[0]
    except Exception:
        return None
    return None


def save_pending_interrupt(thread_id, interrupt_object):
    st.session_state["pending_hitl"] = {
        "thread_id": thread_id,
        "prompt": str(interrupt_object.value),
    }


def sync_pending_interrupt(thread_id):
    pending_interrupt = get_pending_interrupt(thread_id)

    if pending_interrupt is not None:
        save_pending_interrupt(thread_id, pending_interrupt)
    else:
        current_pending = st.session_state.get("pending_hitl")
        if (
            current_pending is not None
            and current_pending.get("thread_id") == thread_id
        ):
            st.session_state["pending_hitl"] = None


def resume_hitl_execution(decision):
    pending_hitl = st.session_state.get("pending_hitl")

    if not pending_hitl:
        st.warning("There is no pending action to approve or reject.")
        return

    interrupted_thread_id = pending_hitl["thread_id"]

    resume_config = {
        "configurable": {"thread_id": interrupted_thread_id},
        "metadata": {"thread_id": interrupted_thread_id},
        "run_name": "hitl_resume_trace",
    }

    try:
        with st.chat_message("assistant", avatar="🤖"):
            status_holder = {
                "box": st.status("🔄 Resuming the requested action...", expanded=True)
            }

            def resumed_ai_only_stream():
                for message_chunk, metadata in chatbot.stream(
                    Command(resume=decision),
                    config=resume_config,
                    stream_mode="messages",
                ):
                    if isinstance(message_chunk, ToolMessage):
                        tool_name = getattr(message_chunk, "name", "tool")
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                    if isinstance(message_chunk, AIMessage):
                        if message_chunk.content:
                            yield message_chunk.content

            resumed_ai_message = st.write_stream(resumed_ai_only_stream())

            next_interrupt = get_pending_interrupt(interrupted_thread_id)

            if next_interrupt is not None:
                save_pending_interrupt(interrupted_thread_id, next_interrupt)
                status_holder["box"].update(
                    label="⚠️ Another approval is required",
                    state="complete",
                    expanded=False,
                )
            else:
                st.session_state["pending_hitl"] = None
                status_holder["box"].update(
                    label="✅ Action completed", state="complete", expanded=False
                )

        if resumed_ai_message:
            st.session_state["message_history"].append(
                {"role": "assistant", "content": resumed_ai_message}
            )

        st.rerun()

    except Exception as error:
        st.error(f"Could not resume the requested action: {error}")


# Session State
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = get_all_threads()

if "pending_hitl" not in st.session_state:
    st.session_state["pending_hitl"] = None

if "thread_titles" not in st.session_state:
    st.session_state["thread_titles"] = {}

add_thread(st.session_state["thread_id"])
sync_pending_interrupt(st.session_state["thread_id"])

# Header
st.markdown(
    """
<div class="nova-header">
    <div class="logo">🤖</div>
    <div>
        <p class="title">Nova Agent</p>
        <p class="subtitle">LangGraph Tool using assistant with RAG & human approval</p>
    </div>
    <div class="status-pill"><span class="dot"></span> Online</div>
</div>
""",
    unsafe_allow_html=True,
)


# Sidebar
with st.sidebar:
    st.markdown("### 💬 Nova Personalised ChatBot")

    if st.button("➕  New chat", use_container_width=True):
        reset_chat()
        st.rerun()

    st.markdown(
        '<div class="sidebar-section-label">Conversations</div>', unsafe_allow_html=True
    )

    search_query = st.text_input(
        "Search conversations",
        placeholder="🔎 Search chats…",
        label_visibility="collapsed",
    )

    for thread_id in st.session_state["chat_threads"][::-1]:
        title = get_thread_title(thread_id)

        if search_query and search_query.lower() not in title.lower():
            continue

        is_active = thread_id == st.session_state["thread_id"]
        label = f"{'💠 ' if is_active else ''}{title}"

        if st.button(label, key=thread_id, use_container_width=True):
            st.session_state["thread_id"] = thread_id
            messages = load_conversation(thread_id)

            temp_messages = []
            for message in messages:
                if isinstance(message, HumanMessage):
                    role = "user"
                elif isinstance(message, AIMessage):
                    role = "assistant"
                else:
                    continue
                temp_messages.append({"role": role, "content": message.content})

            st.session_state["message_history"] = temp_messages
            sync_pending_interrupt(thread_id)
            st.rerun()

    st.markdown("---")
    st.markdown(
        f"""
            <div style="
            background:linear-gradient(135deg,#1e293b,#0f172a);
            padding:14px;
            border-radius:14px;
            border:1px solid rgba(255,255,255,.08);
            margin-top:10px;
            box-shadow:0 4px 12px rgba(0,0,0,.25);
            ">
           
           <p style="color: {"#22C55E" if RAG_INGESTION_AVAILABLE else "#F59E0B"};
           font-weight:600;
           font-size:13px;">
            {
                "🟢 Document Indexed"
                if RAG_INGESTION_AVAILABLE
                else "🟠 Upload PDF"
            }
            </p>

            <p style="margin:8px 0 0 0;color:#94a3b8;font-size:12px;">
            🕒 {datetime.now().strftime("%I:%M %p")} 
                </br> 
            🗓️ {datetime.now().strftime("%d %b %Y")} 
            </p>
            <hr style="border:0;border-top:1px solid rgba(255,255,255,.08);margin:10px 0;">
            <p style="margin:0;text-align:center;font-size:13px;color:white;">
            ❤️ Made by <span style="color:#38bdf8;font-weight:700;">Ankit Gupta 👦</span>
            </p>
            </div>
            """,
        unsafe_allow_html=True,
    )

# Main Chat Area
if not st.session_state["message_history"]:
    st.markdown(
        """
    <div class="empty-state">
        <div class="icon">✨</div>
        <div style="font-size:16px; font-weight:600; color:#e5e7eb;">Start a new conversation</div>
        <div style="font-size:13px; margin-top:4px;">Ask a question, attach a PDF, or try the calculator, weather, or stock tools.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

for message in st.session_state["message_history"]:
    avatar = "🧑" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


# HITL approval interface
pending_hitl = st.session_state.get("pending_hitl")

current_thread_has_pending_hitl = (
    pending_hitl is not None
    and pending_hitl.get("thread_id") == st.session_state["thread_id"]
)

if current_thread_has_pending_hitl:
    st.warning(f"🧑 **Human approval required**\n\n{pending_hitl['prompt']}")

    approve_column, reject_column = st.columns(2)

    with approve_column:
        if st.button(
            "✅ Approve",
            key=f"approve_{st.session_state['thread_id']}",
            type="primary",
            use_container_width=True,
        ):
            resume_hitl_execution("yes")

    with reject_column:
        if st.button(
            "❌ Reject",
            key=f"reject_{st.session_state['thread_id']}",
            use_container_width=True,
        ):
            resume_hitl_execution("no")


# CHAT INPUT + PDF UPLOAD
submission = st.chat_input("Type Here ✨", accept_file=True, file_type=["pdf"])
user_input = None
if submission:

    user_input = submission.text
    uploaded_files = submission.files

    if uploaded_files:
        uploaded_pdf = uploaded_files[0]
        temporary_file_path = None

        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".pdf"
            ) as temporary_file:

                temporary_file.write(uploaded_pdf.getvalue())
                temporary_file_path = temporary_file.name

            with st.spinner(f"Processing {uploaded_pdf.name}..."):

                ingest_rag_document(temporary_file_path)

            st.toast(f"{uploaded_pdf.name} processed successfully.", icon="✅")

        except Exception as error:
            st.error(f"PDF processing failed: {error}")

        finally:
            if temporary_file_path and os.path.exists(temporary_file_path):
                os.remove(temporary_file_path)

if user_input:
    set_thread_title_from_first_message(st.session_state["thread_id"], user_input)

    st.session_state["message_history"].append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_trace",
    }

    with st.chat_message("assistant", avatar="🤖"):
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")

                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

            pending_interrupt = get_pending_interrupt(st.session_state["thread_id"])

            if pending_interrupt is not None:
                save_pending_interrupt(st.session_state["thread_id"], pending_interrupt)
                yield (
                    "\n\n⚠️ This action requires your approval. "
                    "Use the **Approve** or **Reject** button below."
                )

        ai_message = st.write_stream(ai_only_stream())

        if status_holder["box"] is not None:
            if get_pending_interrupt(st.session_state["thread_id"]) is not None:
                status_holder["box"].update(
                    label="⏸️ Waiting for human approval",
                    state="complete",
                    expanded=False,
                )
            else:
                status_holder["box"].update(
                    label="✅ Tool finished", state="complete", expanded=False
                )

    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )

    if (
        st.session_state.get("pending_hitl") is not None
        and st.session_state["pending_hitl"].get("thread_id")
        == st.session_state["thread_id"]
    ):
        st.rerun()

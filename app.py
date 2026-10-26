import streamlit as st
from pathlib import Path
import html
from datetime import datetime, timedelta

from backend.agent import StudyMateAgent
from backend.services.document_service import DocumentService


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI StudyMate",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

DEFAULTS = {
    "agent": None,
    "document_service": None,
    "messages": [],
    "conversations": {},
    "active_conversation_id": "chat_1",
    "usage_count": 0,
    "usage_reset_at": None,
    "document_chunks": [],
    "document_text": "",
    "document_name": "",
    "theme": "Dark",
    "quiz_result": "",
    "summary_result": "",
    "summary_doubt_messages": [],
    "study_plan_result": "",
    "active_page": "💬 Chat Assistant",
    "is_generating": False,
    "summary_doubt_generating": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

if st.session_state.agent is None:
    st.session_state.agent = StudyMateAgent()

if st.session_state.document_service is None:
    st.session_state.document_service = DocumentService()


# --------------------------------------------------
# TEMPORARY SESSION USAGE WINDOW
# --------------------------------------------------

# This is session-only usage tracking, not a permanent per-user quota.

if st.session_state.usage_reset_at is None:
    st.session_state.usage_reset_at = datetime.now() + timedelta(hours=24)

elif datetime.now() >= st.session_state.usage_reset_at:
    st.session_state.usage_count = 0
    st.session_state.usage_reset_at = datetime.now() + timedelta(hours=24)


# --------------------------------------------------
# THEME
# --------------------------------------------------

C = {
    "bg": "#11131B",
    "panel": "#191D29",
    "panel_alt": "#222838",
    "text": "#F4F5FB",
    "muted": "#A8AEC2",
    "border": "#30384A",
    "accent": "#A99BFF",
    "accent_dark": "#8877F2",
    "shadow": "rgba(0, 0, 0, 0.18)",
}


# --------------------------------------------------
# STYLING
# --------------------------------------------------

st.markdown(
    f"""
    <style>
    :root {{
        --sm-bg: {C["bg"]};
        --sm-panel: {C["panel"]};
        --sm-panel-alt: {C["panel_alt"]};
        --sm-text: {C["text"]};
        --sm-muted: {C["muted"]};
        --sm-border: {C["border"]};
        --sm-accent: {C["accent"]};
        --sm-accent-dark: {C["accent_dark"]};
    }}

    .stApp {{
        background: var(--sm-bg);
        color: var(--sm-text);
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    #MainMenu, footer {{
        visibility: hidden;
    }}

    .block-container {{
        max-width: 1250px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }}

    h1, h2, h3, h4, p, label {{
        color: var(--sm-text);
    }}

    section[data-testid="stSidebar"] {{
        background: var(--sm-panel);
        border-right: 1px solid var(--sm-border);
    }}

    section[data-testid="stSidebar"] > div {{
        padding-top: 1.25rem;
    }}

    .brand-wrap {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 4px 18px 4px;
    }}

    .brand-title {{
        color: var(--sm-text);
        font-size: 22px;
        line-height: 1.15;
        font-weight: 800;
        letter-spacing: -0.7px;
    }}

    .brand-subtitle {{
        color: var(--sm-muted);
        font-size: 12px;
        margin-top: 5px;
    }}

    .eyebrow {{
        color: var(--sm-accent);
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1.7px;
        margin-bottom: 8px;
    }}

    .hero-title {{
        color: var(--sm-text);
        font-size: clamp(28px, 4vw, 42px);
        font-weight: 800;
        line-height: 1.16;
        letter-spacing: -1.5px;
        margin: 0 0 10px 0;
    }}

    .hero-description {{
        color: var(--sm-muted);
        font-size: 15px;
        line-height: 1.7;
        margin-bottom: 24px;
    }}

    .welcome-panel {{
        background: linear-gradient(
            135deg,
            var(--sm-panel),
            var(--sm-panel-alt)
        );
        border: 1px solid var(--sm-border);
        border-radius: 22px;
        padding: 26px 28px;
        box-shadow: 0 10px 30px {C["shadow"]};
        margin: 8px 0 22px 0;
    }}

    .welcome-kicker {{
        color: var(--sm-accent);
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}

    .welcome-heading {{
        color: var(--sm-text);
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.7px;
        margin-bottom: 7px;
    }}

    .welcome-copy {{
        color: var(--sm-muted);
        font-size: 14px;
        line-height: 1.65;
    }}

    .feature-card {{
        min-height: 142px;
        background: var(--sm-panel);
        border: 1px solid var(--sm-border);
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 6px 22px {C["shadow"]};
        margin-bottom: 12px;
    }}

    .feature-icon {{
        font-size: 25px;
        margin-bottom: 11px;
    }}

    .feature-title {{
        color: var(--sm-text);
        font-size: 15px;
        font-weight: 750;
        margin-bottom: 6px;
    }}

    .feature-copy {{
        color: var(--sm-muted);
        font-size: 12px;
        line-height: 1.6;
    }}

    .section-heading {{
        color: var(--sm-text);
        font-size: 19px;
        font-weight: 800;
        letter-spacing: -0.4px;
        margin: 20px 0 12px 0;
    }}

    .small-muted {{
        color: var(--sm-muted);
        font-size: 12px;
    }}

    div[data-testid="stChatMessage"] {{
        background: var(--sm-panel);
        border: 1px solid var(--sm-border);
        border-radius: 17px;
        padding: 14px 17px;
        margin-bottom: 10px;
    }}
        /* -----------------------------------------
       CHAT RESPONSE TEXT CONTRAST
    ----------------------------------------- */

    /* Main chat message text */
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {{
        color: #F4F5FB !important;
    }}

    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span,
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong,
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] em {{
        color: #F4F5FB !important;
    }}

    /* Markdown headings */
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1,
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2,
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3,
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h4,
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h5,
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h6 {{
        color: #FFFFFF !important;
        font-weight: 750 !important;
    }}

    /* Lists */
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] ul,
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] ol {{
        color: #F4F5FB !important;
    }}

    /* Links */
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] a {{
        color: #B8ACFF !important;
    }}

    /* Inline code */
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] code {{
        background: #292F40 !important;
        color: #E2DFFF !important;
        border-radius: 5px;
        padding: 2px 5px;
    }}

    /* Code blocks */
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] pre {{
        background: #10131C !important;
        border: 1px solid #30384A !important;
        border-radius: 12px !important;
    }}

    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] pre code {{
        background: transparent !important;
        color: #F4F5FB !important;
    }}

    /* Tables */
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] table {{
        color: #F4F5FB !important;
        border-color: #454D63 !important;
    }}

    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] th {{
        background: #292F40 !important;
        color: #FFFFFF !important;
    }}

    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] td {{
        background: #191D29 !important;
        color: #F4F5FB !important;
    }}

    /* Horizontal separators */
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] hr {{
        border-color: #454D63 !important;
    }}

    /* Chat input outer container */
    div[data-testid="stChatInput"] {{
        background: #191D29 !important;
        border: 1px solid #30384A !important;
        border-radius: 17px !important;
        box-shadow: none !important;
    }}

    /* Chat input wrapper */
    div[data-testid="stChatInput"] > div {{
        background: #191D29 !important;
        border: none !important;
        border-radius: 17px !important;
        box-shadow: none !important;
    }}

    /* Actual text input */
    div[data-testid="stChatInput"] textarea {{
        background: #191D29 !important;
        color: #F4F5FB !important;
        caret-color: #A99BFF !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* Placeholder */
    div[data-testid="stChatInput"] textarea::placeholder {{
        color: #A8AEC2 !important;
        opacity: 1 !important;
    }}

    /* Chat input buttons */
    div[data-testid="stChatInput"] button {{
        background: #222838 !important;
        color: #A99BFF !important;
        border: none !important;
    }}

    /* Bottom chat input area */
    div[data-testid="stBottom"] {{
        background: #11131B !important;
    }}

    div[data-testid="stBottom"] > div {{
        background: #11131B !important;
    }}

    .stButton > button {{
        border-radius: 12px;
        border: 1px solid var(--sm-border);
        background: var(--sm-panel);
        color: var(--sm-text);
        font-weight: 650;
        min-height: 42px;
        transition: all 0.15s ease;
    }}

    .stButton > button:hover {{
        border-color: var(--sm-accent);
        color: var(--sm-accent);
        transform: translateY(-1px);
    }}

    .stButton > button[kind="primary"] {{
        background: var(--sm-accent-dark);
        border-color: var(--sm-accent-dark);
        color: #FFFFFF;
    }}

    .stButton > button[kind="primary"]:hover {{
        background: var(--sm-accent);
        border-color: var(--sm-accent);
        color: #FFFFFF;
    }}

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {{
        background: var(--sm-panel) !important;
        color: var(--sm-text) !important;
        border: 1px solid var(--sm-border) !important;
        border-radius: 12px !important;
    }}

    div[data-testid="stFileUploader"] {{
        background: var(--sm-panel);
        border: 1px dashed var(--sm-border);
        border-radius: 14px;
        padding: 10px;
    }}

    section[data-testid="stSidebar"] div[role="radiogroup"] {{
        gap: 5px;
    }}

    section[data-testid="stSidebar"] div[role="radiogroup"] label {{
        background: transparent;
        border-radius: 11px;
        padding: 8px 10px;
    }}

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
        background: var(--sm-panel-alt);
    }}

    .status-pill {{
        display: inline-block;
        background: var(--sm-panel-alt);
        color: var(--sm-accent);
        border: 1px solid var(--sm-border);
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 750;
    }}

    hr {{
        border-color: var(--sm-border);
    }}

    .app-footer {{
        color: var(--sm-muted);
        text-align: center;
        font-size: 12px;
        padding-top: 30px;
    }}
        /* -----------------------------------------
       DARK PDF UPLOADER
    ----------------------------------------- */

    div[data-testid="stFileUploader"] {{
        background: #191D29 !important;
        border: 1px dashed #454D63 !important;
        border-radius: 14px !important;
        padding: 12px !important;
        color: #F4F5FB !important;
    }}

    /* Inner uploader drop zone */
    div[data-testid="stFileUploader"] section {{
        background: #191D29 !important;
        border: none !important;
        color: #F4F5FB !important;
    }}

    /* Uploader text */
    div[data-testid="stFileUploader"] label,
    div[data-testid="stFileUploader"] span,
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] p {{
        color: #D5D9E6 !important;
    }}

    /* Upload button */
    div[data-testid="stFileUploader"] button {{
        background: #292F40 !important;
        color: #F4F5FB !important;
        border: 1px solid #454D63 !important;
        border-radius: 10px !important;
    }}

    div[data-testid="stFileUploader"] button:hover {{
        background: #353D52 !important;
        border-color: #A99BFF !important;
        color: #A99BFF !important;
    }}

    /* -----------------------------------------
       DARK EXPANDER
    ----------------------------------------- */

    div[data-testid="stExpander"] {{
        background: #191D29 !important;
        border: 1px solid #30384A !important;
        border-radius: 15px !important;
        overflow: hidden !important;
    }}

    div[data-testid="stExpander"] summary {{
        background: #191D29 !important;
        color: #F4F5FB !important;
    }}

    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span {{
        color: #F4F5FB !important;
    }}

    div[data-testid="stExpander"] details {{
        background: #191D29 !important;
    }}

    div[data-testid="stExpander"] details > div {{
        background: #191D29 !important;
    }}

    /* -----------------------------------------
       DARK BOTTOM CHAT AREA
    ----------------------------------------- */

    div[data-testid="stBottom"] {{
        background: #11131B !important;
    }}

    div[data-testid="stBottom"] > div {{
        background: #11131B !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)
# --------------------------------------------------
# REUSABLE DISPLAY HELPERS
# --------------------------------------------------

def page_header(eyebrow, title, description):
    st.markdown(
        f"""
        <div class="eyebrow">{html.escape(eyebrow)}</div>
        <div class="hero-title">{html.escape(title)}</div>
        <div class="hero-description">{html.escape(description)}</div>
        """,
        unsafe_allow_html=True,
    )


def feature_card(icon, title, description):
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{html.escape(title)}</div>
            <div class="feature-copy">{html.escape(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def welcome_panel():
    st.markdown(
        """
        <div class="welcome-panel">
            <div class="welcome-kicker">Your personal learning space</div>
            <div class="welcome-heading">
                Make studying feel a little easier ✨
            </div>
            <div class="welcome-copy">
                Ask questions, understand tricky topics, explore your notes,
                and build a study routine with your AI study companion.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# STUDY MATERIAL UPLOAD HELPER
# --------------------------------------------------

def render_study_material_uploader(widget_key: str):
    """Render an upload control and load a PDF into shared session state."""

    uploaded_file = st.file_uploader(
        "Upload your notes (PDF)",
        type=["pdf"],
        key=widget_key,
        help=(
            "Upload a PDF to use for summaries, quizzes, "
            "and questions about your notes."
        ),
    )

    if uploaded_file is None:
        return

    if uploaded_file.name == st.session_state.document_name:
        st.success(f"{uploaded_file.name} is already loaded.")
        return

    with st.spinner("Reading your study material..."):
        try:
            document_text = (
                st.session_state.document_service.extract_text(uploaded_file)
            )

            if not document_text.strip():
                st.error("No readable text was found in this PDF.")
                return

            chunks = st.session_state.document_service.split_text(
                document_text
            )

            st.session_state.document_text = document_text
            st.session_state.document_chunks = chunks
            st.session_state.document_name = uploaded_file.name
            st.session_state.quiz_result = ""
            st.session_state.summary_result = ""
            st.session_state.summary_doubt_messages = []

            st.success("Your document is ready!")

        except Exception as error:
            st.error(f"Unable to process this PDF: {error}")


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        """
        <div class="brand-wrap">
            <div style="font-size:32px;">📚</div>
            <div>
                <div class="brand-title">AI StudyMate</div>
                <div class="brand-subtitle">
                    Your intelligent study assistant
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Your intelligent study assistant")
    st.divider()

    st.markdown("#### Workspace")

    page = st.radio(
        "Navigation",
        [
            "💬 Chat Assistant",
            "📝 Generate Quiz",
            "📚 Study Planner",
            "📖 Summarize Notes",
        ],
        label_visibility="collapsed",
        key="active_page",
    )

    st.divider()
    st.markdown("#### Recent chats")

    for conversation_id, conversation in list(
        st.session_state.conversations.items()
    )[::-1]:

        chat_label = conversation.get("title", "New chat")[:32]

        if st.button(
            f"💬 {chat_label}",
            key=f"open_{conversation_id}",
            use_container_width=True,
        ):
            st.session_state.active_conversation_id = conversation_id
            st.session_state.messages = conversation.get("messages", [])
            st.session_state.active_page = "💬 Chat Assistant"
            st.rerun()

    if st.button("＋ New chat", use_container_width=True):

        new_id = f"chat_{len(st.session_state.conversations) + 1}"

        st.session_state.conversations[new_id] = {
            "title": "New chat",
            "messages": [],
        }

        st.session_state.active_conversation_id = new_id
        st.session_state.messages = []
        st.session_state.active_page = "💬 Chat Assistant"
        st.rerun()

    st.divider()
    st.markdown("#### Study material")

    render_study_material_uploader("sidebar_pdf_uploader")

    if st.session_state.document_name:
        st.caption(f"Loaded: {st.session_state.document_name}")

    st.divider()

    st.caption(
        f"Session usage: {st.session_state.usage_count}/20 requests"
    )

    if st.button(
        "🗑️ Clear current chat",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()
        # --------------------------------------------------
# CHAT ASSISTANT
# --------------------------------------------------
# --------------------------------------------------
# CHAT ASSISTANT
# --------------------------------------------------

if page == "💬 Chat Assistant":

    page_header(
        "AI STUDY ASSISTANT",
        "What would you like to learn?",
        (
            "Ask a question, explore a concept, "
            "or get help from your uploaded notes."
        ),
    )

    # --------------------------------------------------
    # UPLOAD NOTES DIRECTLY IN CHAT
    # --------------------------------------------------

    with st.expander(
        "📎 Upload notes to ask questions about them",
        expanded=not bool(st.session_state.document_name),
    ):

        render_study_material_uploader("chat_pdf_uploader")

        if st.session_state.document_name:

            st.markdown(
                f"""
                <div class="status-pill">
                    📄 {html.escape(st.session_state.document_name)} loaded
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "Remove uploaded notes",
                key="remove_chat_document",
            ):

                st.session_state.document_text = ""
                st.session_state.document_chunks = []
                st.session_state.document_name = ""

                st.session_state.summary_result = ""
                st.session_state.quiz_result = ""
                st.session_state.summary_doubt_messages = []

                st.rerun()

    # --------------------------------------------------
    # WELCOME SCREEN
    # --------------------------------------------------

    if not st.session_state.messages:

        welcome_panel()

        st.markdown(
            '<div class="section-heading">Quick starters</div>',
            unsafe_allow_html=True,
        )

        suggestions = [
            (
                "🧠 Explain a concept",
                (
                    "Explain machine learning in simple language "
                    "with a real-world example."
                ),
            ),
            (
                "📄 Help with my notes",
                "Explain the key concepts in my uploaded notes.",
            ),
            (
                "📝 Practice questions",
                "Create practice questions to help me revise.",
            ),
            (
                "🔎 Give me an example",
                (
                    "Explain a difficult academic concept "
                    "using a simple example."
                ),
            ),
        ]

        columns = st.columns(2)

        for index, (label, query) in enumerate(suggestions):

            with columns[index % 2]:

                if st.button(
                    label,
                    use_container_width=True,
                    key=f"suggestion_{index}",
                ):

                    st.session_state.pending_query = query
                    st.rerun()

    # --------------------------------------------------
    # DISPLAY CHAT HISTORY
    # --------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --------------------------------------------------
    # CHAT INPUT
    # --------------------------------------------------

    pending_query = st.session_state.pop(
        "pending_query",
        None,
    )

    user_query = st.chat_input(
        (
            "StudyMate is responding..."
            if st.session_state.is_generating
            else "Ask StudyMate anything..."
        ),
        disabled=st.session_state.is_generating,
    )

    if pending_query and not st.session_state.is_generating:
        user_query = pending_query

    # --------------------------------------------------
    # USAGE LIMIT
    # --------------------------------------------------

    if st.session_state.usage_count >= 20:

        st.warning(
            "You've reached the temporary session limit of 20 chat requests. "
            "Start a new session or return after the reset window."
        )

    # --------------------------------------------------
    # GENERATE RESPONSE
    # --------------------------------------------------

    if (
        user_query
        and not st.session_state.is_generating
        and st.session_state.usage_count < 20
    ):

        st.session_state.is_generating = True
        st.session_state.usage_count += 1

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_query,
            }
        )

        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):

            try:

                with st.spinner("StudyMate is thinking..."):

                    response = st.session_state.agent.chat(
                        query=user_query,
                        history=st.session_state.messages[:-1],
                        document_chunks=st.session_state.document_chunks,
                    )

                st.markdown(response)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                    }
                )

                active_id = (
                    st.session_state.active_conversation_id
                )

                st.session_state.conversations[active_id] = {
                    "title": user_query[:32] or "New chat",
                    "messages": st.session_state.messages,
                }

            except Exception as error:

                st.error(
                    "Unable to generate a response. Please check your "
                    "API key and internet connection."
                )

                st.caption(str(error))

            finally:

                st.session_state.is_generating = False


# --------------------------------------------------
# QUIZ GENERATOR
# --------------------------------------------------

elif page == "📝 Generate Quiz":

    page_header(
        "ACTIVE RECALL",
        "Quiz Generator",
        (
            "Turn your notes into practice questions "
            "and strengthen your memory."
        ),
    )

    if st.session_state.document_text:

        feature_card(
            "🎯",
            "Practice what you have learned",
            (
                "Generate five multiple-choice questions "
                "with correct answers and explanations."
            ),
        )

        if st.button(
            "✨ Generate 5 MCQs",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner("Creating your quiz..."):

                try:

                    st.session_state.quiz_result = (
                        st.session_state.agent.generate_quiz(
                            st.session_state.document_text
                        )
                    )

                except Exception as error:

                    st.error("Unable to generate quiz.")
                    st.caption(str(error))

        if st.session_state.quiz_result:

            st.markdown("---")
            st.markdown(st.session_state.quiz_result)

    else:

        feature_card(
            "📄",
            "Upload your study material first",
            (
                "Add a PDF from the sidebar to generate "
                "a quiz from your own notes."
            ),
        )


# --------------------------------------------------
# STUDY PLANNER
# --------------------------------------------------

elif page == "📚 Study Planner":

    page_header(
        "PLAN YOUR LEARNING",
        "Study Planner",
        (
            "Build a balanced schedule with time for learning, "
            "practice, and revision."
        ),
    )

    feature_card(
        "🗓️",
        "A plan that fits your pace",
        "Tell StudyMate what you need to cover and how much time you have.",
    )

    with st.form("study_plan_form"):

        topics = st.text_area(
            "Topics to study",
            placeholder=(
                "Example: Artificial Intelligence, Machine Learning, "
                "Neural Networks"
            ),
            height=140,
        )

        col1, col2 = st.columns(2)

        with col1:

            days = st.number_input(
                "Available days",
                min_value=1,
                max_value=90,
                value=7,
            )

        with col2:

            hours_per_day = st.number_input(
                "Study hours per day",
                min_value=1,
                max_value=12,
                value=3,
            )

        submitted = st.form_submit_button(
            "✨ Create my study plan",
            type="primary",
            use_container_width=True,
        )

    if submitted:

        if not topics.strip():

            st.warning("Please enter the topics you want to study.")

        else:

            with st.spinner("Creating your study plan..."):

                try:

                    st.session_state.study_plan_result = (
                        st.session_state.agent.generate_study_plan(
                            topics,
                            days,
                            hours_per_day,
                        )
                    )

                except Exception as error:

                    st.error("Unable to generate study plan.")
                    st.caption(str(error))

    if st.session_state.study_plan_result:

        st.markdown("---")
        st.markdown(st.session_state.study_plan_result)
        # --------------------------------------------------
# SUMMARIZE NOTES
# --------------------------------------------------

elif page == "📖 Summarize Notes":

    page_header(
        "SMART NOTES",
        "Summarize Notes",
        (
            "Turn lengthy study material into a clearer, "
            "more revision-friendly summary."
        ),
    )

    render_study_material_uploader("summarize_pdf_uploader")

    if st.session_state.document_text:

        feature_card(
            "✨",
            "Make your notes easier to revise",
            (
                "Create a summary with main concepts, definitions, "
                "key points, and a conclusion."
            ),
        )

        if st.button(
            "✨ Generate summary",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner("Summarizing your study material..."):

                try:

                    st.session_state.summary_result = (
                        st.session_state.agent.summarize(
                            st.session_state.document_text
                        )
                    )

                except Exception as error:

                    st.error("Unable to generate summary.")
                    st.caption(str(error))

        if st.session_state.summary_result:

            st.markdown("---")
            st.markdown(st.session_state.summary_result)

            st.markdown("### 💬 Ask a follow-up doubt")

            st.caption(
                "Ask questions about the summary or uploaded notes. "
                "Your summary will stay visible while you continue asking."
            )

            for message in st.session_state.summary_doubt_messages:

                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            doubt = st.chat_input(
                "Ask a doubt about these notes...",
                key="summary_doubt_input",
                disabled=st.session_state.summary_doubt_generating,
            )

            if (
                doubt
                and not st.session_state.summary_doubt_generating
            ):

                st.session_state.summary_doubt_messages.append(
                    {
                        "role": "user",
                        "content": doubt,
                    }
                )

                st.session_state.summary_doubt_generating = True

                with st.chat_message("user"):
                    st.markdown(doubt)

                with st.chat_message("assistant"):

                    try:

                        with st.spinner(
                            "StudyMate is answering your doubt..."
                        ):

                            answer = st.session_state.agent.chat(
                                query=(
                                    "Answer the student's follow-up question "
                                    "using the uploaded study material and "
                                    "generated summary. If the material does "
                                    "not contain the answer, use your general "
                                    "knowledge to provide a helpful answer. "
                                    "Clearly distinguish the document content "
                                    "from additional explanation when needed."
                                    "\n\n"
                                    f"GENERATED SUMMARY:\n"
                                    f"{st.session_state.summary_result}\n\n"
                                    f"STUDENT QUESTION:\n{doubt}"
                                ),
                                history=(
                                    st.session_state
                                    .summary_doubt_messages[:-1]
                                ),
                                document_chunks=(
                                    st.session_state.document_chunks
                                ),
                            )

                        st.markdown(answer)

                        st.session_state.summary_doubt_messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                            }
                        )

                    except Exception as error:

                        st.error("Unable to answer this doubt.")
                        st.caption(str(error))

                    finally:

                        st.session_state.summary_doubt_generating = False

                st.rerun()

    else:

        feature_card(
            "📄",
            "Upload your notes to begin",
            "Upload a PDF above, then generate a summary of its content.",
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="app-footer">
        AI StudyMate · Learn a little better, every day ✨
    </div>
    """,
    unsafe_allow_html=True,
)
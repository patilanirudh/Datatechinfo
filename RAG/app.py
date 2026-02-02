import streamlit as st
from rag_pipeline import RAGPipeline
import tempfile
import os

# MUST be first Streamlit command
st.set_page_config(
    page_title="AI Doc Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Optimized CSS (minified)
st.markdown("""<style>
.stButton>button{background:linear-gradient(90deg,#FF4B4B 0%,#FF6B6B 100%);color:white;border:none;border-radius:8px;padding:0.5rem 1.5rem;font-weight:600;transition:all 0.3s}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(255,75,75,0.4)}
</style>""", unsafe_allow_html=True)

# Cache RAG initialization (expensive operation)
@st.cache_resource(show_spinner="🔄 Initializing AI...")
def get_rag_pipeline():
    """Cached RAG pipeline - loads only once"""
    return RAGPipeline()

# Initialize session state
def init_state():
    if 'ready' not in st.session_state:
        st.session_state.ready = False
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_doc' not in st.session_state:
        st.session_state.current_doc = None
    if 'doc_hash' not in st.session_state:
        st.session_state.doc_hash = None

init_state()

# Get cached RAG pipeline
rag = get_rag_pipeline()

# Sidebar
with st.sidebar:
    st.title("📄 Document")
    
    uploaded_file = st.file_uploader(
        "Upload PDF/TXT",
        type=['pdf', 'txt'],
        label_visibility="collapsed",
        key="file_uploader"
    )
    
    # Check if new document
    current_hash = hash(uploaded_file.getvalue()) if uploaded_file else None
    is_new_doc = current_hash != st.session_state.doc_hash
    
    if uploaded_file and is_new_doc:
        if st.button("⚡ Process Document", use_container_width=True, type="primary"):
            with st.spinner("⏳ Processing..."):
                try:
                    # Reset for new document
                    rag.reset()
                    
                    # Save temp file
                    suffix = os.path.splitext(uploaded_file.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    # Process document
                    docs = rag.load_documents(tmp_path)
                    rag.create_vectorstore(docs)
                    rag.setup_qa_chain()
                    
                    # Update state
                    st.session_state.ready = True
                    st.session_state.messages = []
                    st.session_state.current_doc = uploaded_file.name
                    st.session_state.doc_hash = current_hash
                    
                    # Cleanup
                    os.unlink(tmp_path)
                    
                    st.success(f"✅ Ready! ({len(docs)} chunks)")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    
    # Status indicator
    if st.session_state.ready:
        st.success("🟢 Ready")
        if st.session_state.current_doc:
            st.caption(f"📄 {st.session_state.current_doc}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Summary", use_container_width=True):
                st.session_state.quick_query = "Provide a clear 3-point summary"
        with col2:
            if st.button("🔑 Key Points", use_container_width=True):
                st.session_state.quick_query = "List the main key points"
        
        if st.button("🔄 New Doc", use_container_width=True):
            rag.reset()
            st.session_state.ready = False
            st.session_state.messages = []
            st.session_state.current_doc = None
            st.session_state.doc_hash = None
            st.rerun()
    else:
        st.warning("🔴 Upload document")

# Main chat area
st.title("🤖 AI Document Chat")

if st.session_state.ready:
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and msg.get("sources"):
                    with st.expander("📚 Sources", expanded=False):
                        for i, src in enumerate(msg["sources"][:3], 1):  # Limit to 3
                            st.caption(f"**{i}.** {src[:250]}...")
    
    # Process quick query
    if hasattr(st.session_state, 'quick_query') and st.session_state.quick_query:
        prompt = st.session_state.quick_query
        st.session_state.quick_query = None
        
        # Add to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get response
        with st.spinner("🤔 Analyzing..."):
            try:
                answer, sources = rag.query(prompt)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": [d.page_content for d in sources]
                })
            except Exception as e:
                st.error(f"❌ {str(e)}")
        
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask about your document...", key="chat_input"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    answer, sources = rag.query(prompt)
                    st.markdown(answer)
                    
                    if sources:
                        with st.expander("📚 Sources", expanded=False):
                            for i, doc in enumerate(sources[:3], 1):
                                st.caption(f"**{i}.** {doc.page_content[:250]}...")
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": [d.page_content for d in sources]
                        })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer
                        })
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    
        st.rerun()

else:
    # Welcome screen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**🔒 Private**\nRuns locally")
    with col2:
        st.info("**⚡ Fast**\nOptimized RAG")
    with col3:
        st.info("**🎯 Smart**\nCustom AI model")
    
    st.markdown("---")
    st.markdown("### 🚀 Quick Start")
    st.markdown("""
    1. **Upload** a PDF or TXT file (sidebar →)
    2. Click **Process Document**
    3. **Ask questions** or use Quick Actions
    """)
    
    st.markdown("---")
    st.caption("💡 Powered by rag-assistant • Requires: `ollama serve`")
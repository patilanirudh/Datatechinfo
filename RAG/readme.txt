# RAG Chatbot

A local, private RAG (Retrieval-Augmented Generation) application that lets you chat with your documents using AI.

## What This Does

-  Upload PDF or TXT files
- **Ask questions** about your documents
- **Get AI-powered answers** with source citations
- **100% private** - runs entirely on your local machine

---

## 🛠️ Prerequisites

### 1. Python 3.8+
```bash
python --version  # Should be 3.8 or higher
```

### 2. Ollama (Local LLM Engine)
Install from: https://ollama.com/download

---

## 📦 Installation

### Step 1: Install Python Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install required packages
pip install streamlit langchain langchain-community chromadb sentence-transformers pypdf
```

### Step 2: Install & Setup Ollama

#### Install Ollama
- **Windows/Mac**: Download from https://ollama.com/download
- **Linux**: 
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Pull Required AI Model
```bash
# Start Ollama service (in separate terminal)
ollama serve

# Pull the model (in another terminal)
ollama pull llama3.2:3b

# OR use a smaller model for faster responses
ollama pull gemma2:2b

# Create custom model for RAG (optional but recommended)
ollama create rag-assistant -f Modelfile
```

#### Create Modelfile (Optional - for better RAG performance)
Create a file named `Modelfile`:
```
FROM llama3.2:3b
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
SYSTEM You are a helpful document assistant. Answer questions accurately based only on the provided context. Be concise and cite sources when possible.
```

Then create the custom model:
```bash
ollama create rag-assistant -f Modelfile
```

---

## 🚀 Running the Application

### Terminal 1: Start Ollama Server
```bash
ollama serve
```
*Keep this terminal running in the background*

### Terminal 2: Run the Streamlit App
```bash
# Make sure virtual environment is activated
streamlit run app.py
```

### Terminal 3: Check Available Models (Optional)
```bash
ollama list
```

---

## 📖 Usage Guide

### 1. **Upload Document**
   - Click "Browse files" in sidebar
   - Select a PDF or TXT file
   - Click "⚡ Process Document"
   - Wait for "✅ Ready!" message

### 2. **Ask Questions**
   - Type your question in the chat box
   - Press Enter
   - View AI answer with source citations

### 3. **Quick Actions**
   - **📝 Summary**: Get a 3-point summary
   - **🔑 Key Points**: List main points
   - **🔄 New Doc**: Process a different document

### 4. **Example Questions**
   ```
   - "What is the main topic of this document?"
   - "Summarize the key findings"
   - "Explain [specific concept] from the document"
   - "What does the document say about [topic]?"
   ```

---





## 🛑 Stopping the Application

### Method 1: Graceful Shutdown
```bash
# In Streamlit terminal: Press Ctrl+C
# In Ollama terminal: Press Ctrl+C
```

### Method 2: Force Kill

**Windows:**
```bash
# Kill Streamlit
taskkill /F /IM python.exe

# Kill Ollama
taskkill /F /IM ollama.exe
```


### Method 3: Check & Kill by Port
```bash
# Find process on port 8501 (Streamlit)
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8501 | xargs kill -9

# Find process on port 11434 (Ollama)
# Windows:
netstat -ano | findstr :11434
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:11434 | xargs kill -9
```

---

## ⚙️ Configuration

### Change Model in `rag_pipeline.py`
```python
# Line 29 - Change model name
self.llm = Ollama(
    model="llama3.2:3b",  # Change this to your model
    # ...
)
```

### Adjust Chunk Size (for better accuracy)
```python
# Line 81-87 in rag_pipeline.py
if total_length < 3000:
    chunk_size, chunk_overlap = 400, 80  # Increase for longer context
```

### Change Number of Retrieved Chunks
```python
# Line 116 in rag_pipeline.py
search_kwargs={
    "k": 4,  # Increase to 6-8 for more context
}



from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import List, Tuple
from functools import lru_cache
import uuid
import gc

class RAGPipeline:
    """Optimized RAG Pipeline with caching and performance improvements"""
    
    # Class-level cache for embeddings (shared across instances)
    _embeddings_cache = None
    
    def __init__(self, model_name: str = "rag-assistant"):
        """Initialize RAG Pipeline with lazy loading"""
        # Lazy load embeddings (expensive operation)
        if RAGPipeline._embeddings_cache is None:
            print("🔄 Loading embeddings model (one-time)...")
            RAGPipeline._embeddings_cache = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={
                    'normalize_embeddings': True,
                    'batch_size': 32  # Batch processing for speed
                }
            )
        
        self.embeddings = RAGPipeline._embeddings_cache
        
        # Optimized LLM with streaming
        self.llm = Ollama(
            model=model_name,
            base_url="http://localhost:11434",
            temperature=0.1,
            top_p=0.9,
            num_ctx=4096,
            num_predict=512,  # Limit response length
            repeat_penalty=1.1  # Reduce repetition
        )
        
        self.vectorstore = None
        self.chain = None
        self.retriever = None
        self.db_dir = "./chroma_db"
        self.current_collection = None
        
    def _clear_vectorstore(self):
        """Efficient vectorstore cleanup"""
        if self.vectorstore and self.current_collection:
            try:
                self.vectorstore._client.delete_collection(self.current_collection)
            except Exception:
                pass
            finally:
                self.vectorstore = None
        gc.collect()
        
    def load_documents(self, file_path: str) -> List:
        """Optimized document loading with smart chunking"""
        # Fast loader selection
        loader = PyPDFLoader(file_path) if file_path.endswith('.pdf') else TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        
        if not documents or sum(len(d.page_content) for d in documents) == 0:
            raise ValueError("Document is empty or unreadable")
        
        # Smart chunking based on content length
        total_length = sum(len(d.page_content) for d in documents)
        
        if total_length < 3000:
            chunk_size, chunk_overlap = 400, 80
        elif total_length < 10000:
            chunk_size, chunk_overlap = 700, 140
        else:
            chunk_size, chunk_overlap = 1000, 200
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
            length_function=len,
        )
        
        # Filter out tiny chunks
        chunks = [c for c in splitter.split_documents(documents) 
                  if len(c.page_content.strip()) > 30]
        
        if not chunks:
            raise ValueError("No valid chunks created")
        
        return chunks
    
    def create_vectorstore(self, documents: List):
        """Optimized vectorstore creation"""
        if not documents:
            raise ValueError("No documents provided")
        
        self._clear_vectorstore()
        self.current_collection = f"doc_{uuid.uuid4().hex[:8]}"
        
        # Batch embedding for speed
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.db_dir,
            collection_name=self.current_collection,
            collection_metadata={"hnsw:space": "cosine"}
        )
        
    def setup_qa_chain(self):
        """Setup optimized QA chain"""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized")
        
        # Efficient retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 4,  # Reduced for speed
                "fetch_k": 12,
                "lambda_mult": 0.7
            }
        )
        
        # Concise, focused prompt
        prompt = ChatPromptTemplate.from_template(
            """Answer the question based on the context below. Be concise and accurate.

Context: {context}

Question: {question}

Answer:"""
        )
        
        self.chain = (
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
    def _format_docs(self, docs: List) -> str:
        """Efficient document formatting"""
        return "\n\n".join(d.page_content for d in docs)
    
    @lru_cache(maxsize=100)
    def _cached_query(self, question: str) -> str:
        """Cache frequent queries"""
        return self.chain.invoke(question)
        
    def query(self, question: str) -> Tuple[str, List]:
        """Execute query with caching"""
        if not self.chain:
            raise ValueError("QA chain not initialized")
        
        # Get answer (with caching for repeated queries)
        try:
            answer = self._cached_query(question)
        except TypeError:
            # If caching fails, query directly
            answer = self.chain.invoke(question)
        
        # Get sources
        sources = self.retriever.invoke(question)
        
        return answer, sources
    
    def reset(self):
        """Full pipeline reset"""
        self._clear_vectorstore()
        self.chain = None
        self.retriever = None
        self.current_collection = None
        self._cached_query.cache_clear()  # Clear query cache
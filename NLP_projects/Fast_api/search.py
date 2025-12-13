from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import json
import uuid
from datetime import datetime
from enum import Enum
import logging
from contextlib import asynccontextmanager
import httpx
import os
from dataclasses import dataclass, asdict
import re
from urllib.parse import urljoin, urlparse
# import aiohttp
# from bs4 import BeautifulSoup
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentType(str, Enum):
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"

@dataclass
class Message:
    id: str
    sender: str
    receiver: str
    content: str
    timestamp: datetime
    message_type: str = "text"

@dataclass
class Task:
    id: str
    description: str
    status: TaskStatus
    assigned_agent: Optional[str]
    result: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    domain: str
    relevance_score: float

@dataclass
class ResearchOutput:
    query: str
    summary: str
    key_findings: List[str]
    sources: List[SearchResult]
    confidence_score: float
    timestamp: datetime

class TaskRequest(BaseModel):
    description: str
    task_type: str = "research"
    priority: int = 1

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[str] = None
    assigned_agent: Optional[str] = None
    sources: Optional[List[Dict]] = None

# Agent Base Class
class BaseAgent:
    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.is_busy = False
        self.capabilities = []
        self.message_queue = asyncio.Queue()
        
    async def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming message and return response"""
        raise NotImplementedError
    
    async def execute_task(self, task: Task) -> str:
        """Execute assigned task"""
        raise NotImplementedError
    
    async def start_listening(self):
        """Start listening for messages"""
        while True:
            try:
                message = await self.message_queue.get()
                response = await self.process_message(message)
                if response:
                    await agent_manager.send_message(response)
            except Exception as e:
                logger.error(f"Agent {self.agent_id} error: {e}")
                await asyncio.sleep(1)

# Coordinator Agent
class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("coordinator", AgentType.COORDINATOR)
        self.capabilities = ["task_distribution", "coordination", "query_optimization"]
    
    async def process_message(self, message: Message) -> Optional[Message]:
        logger.info(f"Coordinator processing: {message.content}")
        
        if message.message_type == "task_request":
            await self.distribute_task(message)
            return None
        elif message.message_type == "task_result":
            return await self.handle_task_result(message)
        
        return None
    
    async def distribute_task(self, message: Message):
        """Distribute task to research agent"""
        content = json.loads(message.content)
        task_id = content.get("task_id")
        description = content.get("description", "")
        
        # Optimize the query for better search results
        optimized_query = await self.optimize_query(description)
        
        # Update task status to processing
        if task_id in agent_manager.tasks:
            agent_manager.tasks[task_id].status = TaskStatus.PROCESSING
            agent_manager.tasks[task_id].assigned_agent = "researcher"
        
        # Create and send task assignment message
        task_message = Message(
            id=str(uuid.uuid4()),
            sender=self.agent_id,
            receiver="researcher",
            content=json.dumps({
                "task_id": task_id,
                "original_query": description,
                "optimized_query": optimized_query,
                "task_type": content.get("task_type", "research")
            }),
            timestamp=datetime.now(),
            message_type="task_assignment"
        )
        
        await agent_manager.send_message(task_message)
    
    async def optimize_query(self, query: str) -> str:
        """Optimize query for better search results"""
        # Remove common stop words and optimize for search
        stop_words = {"what", "how", "when", "where", "why", "who", "is", "are", "was", "were", "the", "a", "an"}
        
        # Extract key terms
        words = query.lower().split()
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Add context terms for better results
        if any(word in query.lower() for word in ["latest", "recent", "current", "new"]):
            key_terms.append("2024")
        
        return " ".join(key_terms[:5])  # Limit to 5 key terms
    
    async def handle_task_result(self, message: Message) -> Optional[Message]:
        """Handle completed task results"""
        logger.info(f"Task completed by {message.sender}")
        return None
    
    async def execute_task(self, task: Task) -> str:
        return f"Task {task.id} coordinated and distributed to research agent"

# Research Agent with Web Search
class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("researcher", AgentType.RESEARCHER)
        self.capabilities = ["web_search", "data_gathering", "source_validation", "content_analysis"]
        self.search_engines = {
            "duckduckgo": "https://api.duckduckgo.com/",
            "serp": "https://serpapi.com/search.json"
        }
    
    async def process_message(self, message: Message) -> Optional[Message]:
        if message.message_type == "task_assignment":
            content = json.loads(message.content)
            task_id = content.get("task_id")
            original_query = content.get("original_query", "")
            optimized_query = content.get("optimized_query", "")
            
            # Update task status to processing
            if task_id in agent_manager.tasks:
                agent_manager.tasks[task_id].status = TaskStatus.PROCESSING
                agent_manager.tasks[task_id].assigned_agent = self.agent_id
            
            try:
                # Perform comprehensive research
                research_result = await self.conduct_comprehensive_research(original_query, optimized_query)
                
                # Update task with result
                await agent_manager.process_task_result(task_id, research_result, self.agent_id)
                
                return Message(
                    id=str(uuid.uuid4()),
                    sender=self.agent_id,
                    receiver="coordinator",
                    content=json.dumps({"result": research_result, "task_id": task_id}),
                    timestamp=datetime.now(),
                    message_type="task_result"
                )
            except Exception as e:
                logger.error(f"Research failed: {e}")
                await agent_manager.process_task_error(task_id, str(e), self.agent_id)
                return None
        
        return None
    
    async def conduct_comprehensive_research(self, original_query: str, optimized_query: str) -> str:
        """Conduct comprehensive research with multiple sources"""
        
        # Perform multiple searches
        search_results = []
        
        # Search with original query
        results1 = await self.search_web(original_query)
        search_results.extend(results1)
        
        # Search with optimized query
        results2 = await self.search_web(optimized_query)
        search_results.extend(results2)
        
        # Remove duplicates and rank by relevance
        unique_results = self.deduplicate_results(search_results)
        ranked_results = self.rank_results(unique_results, original_query)
        
        # Validate sources
        validated_results = await self.validate_sources(ranked_results[:10])  # Top 10 results
        
        # Generate comprehensive response
        research_output = await self.generate_research_output(
            original_query, 
            validated_results
        )
        
        return self.format_research_response(research_output)
    
    async def search_web(self, query: str) -> List[SearchResult]:
        """Search the web using multiple methods"""
        results = []
        
        # Method 1: Simulated web search (replace with actual API calls)
        simulated_results = await self.simulate_web_search(query)
        results.extend(simulated_results)
        
        # Method 2: You can add real search API calls here
        # For production, integrate with Google Custom Search API, Bing API, etc.
        
        return results
    
    async def simulate_web_search(self, query: str) -> List[SearchResult]:
        """Simulate web search results (replace with actual search API)"""
        await asyncio.sleep(1)  # Simulate network delay
        
        # This is a simulation - in production, use real search APIs
        mock_results = [
            SearchResult(
                title=f"Comprehensive Guide to {query}",
                url=f"https://example.com/guide-{query.replace(' ', '-')}",
                snippet=f"This comprehensive guide covers everything you need to know about {query}, including latest developments and expert insights.",
                domain="example.com",
                relevance_score=0.95
            ),
            SearchResult(
                title=f"Latest Research on {query}",
                url=f"https://research.edu/latest-{query.replace(' ', '-')}",
                snippet=f"Recent academic research and findings related to {query} from leading institutions and researchers.",
                domain="research.edu",
                relevance_score=0.90
            ),
            SearchResult(
                title=f"Expert Analysis: {query}",
                url=f"https://experts.org/analysis-{query.replace(' ', '-')}",
                snippet=f"Expert analysis and professional insights on {query} with practical implications and recommendations.",
                domain="experts.org",
                relevance_score=0.85
            ),
            SearchResult(
                title=f"News and Updates: {query}",
                url=f"https://news.com/updates-{query.replace(' ', '-')}",
                snippet=f"Latest news and updates about {query} from reliable news sources and industry publications.",
                domain="news.com",
                relevance_score=0.80
            ),
            SearchResult(
                title=f"Case Studies: {query}",
                url=f"https://casestudies.org/examples-{query.replace(' ', '-')}",
                snippet=f"Real-world case studies and examples related to {query} with detailed analysis and outcomes.",
                domain="casestudies.org",
                relevance_score=0.75
            )
        ]
        
        return mock_results
    
    def deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results based on URL and title similarity"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        return unique_results
    
    def rank_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Rank results by relevance and source quality"""
        # Sort by relevance score and domain authority
        domain_scores = {
            ".edu": 0.9,
            ".gov": 0.95,
            ".org": 0.8,
            ".com": 0.7
        }
        
        def calculate_score(result: SearchResult) -> float:
            base_score = result.relevance_score
            
            # Domain authority bonus
            for domain, bonus in domain_scores.items():
                if domain in result.domain:
                    base_score += bonus * 0.1
                    break
            
            # Query term matching bonus
            query_terms = query.lower().split()
            title_matches = sum(1 for term in query_terms if term in result.title.lower())
            snippet_matches = sum(1 for term in query_terms if term in result.snippet.lower())
            
            base_score += (title_matches * 0.05) + (snippet_matches * 0.02)
            
            return base_score
        
        return sorted(results, key=calculate_score, reverse=True)
    
    async def validate_sources(self, results: List[SearchResult]) -> List[SearchResult]:
        """Validate source credibility and accessibility"""
        validated = []
        
        for result in results:
            # Simulate source validation
            if await self.is_source_valid(result):
                validated.append(result)
        
        return validated
    
    async def is_source_valid(self, result: SearchResult) -> bool:
        """Check if source is valid and accessible"""
        # In production, implement actual URL checking, SSL verification, etc.
        await asyncio.sleep(0.1)  # Simulate validation time
        
        # Simple validation rules
        if any(domain in result.domain for domain in [".edu", ".gov", ".org"]):
            return True
        
        if result.relevance_score > 0.7:
            return True
        
        return False
    
    async def generate_research_output(self, query: str, results: List[SearchResult]) -> ResearchOutput:
        """Generate comprehensive research output"""
        
        # Extract key findings
        key_findings = []
        for i, result in enumerate(results[:5], 1):
            key_findings.append(f"Finding {i}: {result.snippet}")
        
        # Generate summary
        summary = f"Based on research from {len(results)} validated sources, here are the key insights about '{query}':\n\n"
        summary += "The research reveals comprehensive information addressing your query with multiple perspectives and expert analysis. "
        summary += "The findings are supported by credible sources including educational institutions, research organizations, and industry experts."
        
        # Calculate confidence score
        confidence_score = min(0.95, sum(r.relevance_score for r in results) / len(results) if results else 0.5)
        
        return ResearchOutput(
            query=query,
            summary=summary,
            key_findings=key_findings,
            sources=results,
            confidence_score=confidence_score,
            timestamp=datetime.now()
        )
    
    def format_research_response(self, research: ResearchOutput) -> str:
        """Format research output for user consumption"""
        
        response = f"# Research Results for: {research.query}\n\n"
        response += f"**Summary:**\n{research.summary}\n\n"
        
        response += f"**Key Findings:**\n"
        for finding in research.key_findings:
            response += f"• {finding}\n"
        
        response += f"\n**Sources (Confidence Score: {research.confidence_score:.2f}):**\n"
        for i, source in enumerate(research.sources, 1):
            response += f"{i}. **{source.title}** ({source.domain})\n"
            response += f"   - URL: {source.url}\n"
            response += f"   - Relevance: {source.relevance_score:.2f}\n"
            response += f"   - Excerpt: {source.snippet}\n\n"
        
        response += f"**Research completed at:** {research.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        response += f"**Total sources analyzed:** {len(research.sources)}\n"
        
        return response
    
    async def execute_task(self, task: Task) -> str:
        return await self.conduct_comprehensive_research(task.description, task.description)

# Agent Manager
class AgentManager:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.message_history: List[Message] = []
        
    async def initialize_agents(self):
        """Initialize coordinator and research agents"""
        agents = [
            CoordinatorAgent(),
            ResearchAgent()
        ]
        
        for agent in agents:
            self.agents[agent.agent_id] = agent
            asyncio.create_task(agent.start_listening())
        
        logger.info(f"Initialized {len(agents)} agents: {list(self.agents.keys())}")
    
    async def send_message(self, message: Message):
        """Send message to target agent"""
        if message.receiver in self.agents:
            await self.agents[message.receiver].message_queue.put(message)
            self.message_history.append(message)
        else:
            logger.error(f"Agent {message.receiver} not found")
    
    async def create_task(self, description: str, task_type: str = "research") -> str:
        """Create new research task"""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            description=description,
            status=TaskStatus.PENDING,
            assigned_agent=None,
            result=None,
            created_at=datetime.now(),
            metadata={"task_type": task_type}
        )
        
        self.tasks[task_id] = task
        
        # Send task to coordinator
        message = Message(
            id=str(uuid.uuid4()),
            sender="system",
            receiver="coordinator",
            content=json.dumps({
                "task_id": task_id,
                "description": description,
                "task_type": task_type
            }),
            timestamp=datetime.now(),
            message_type="task_request"
        )
        
        await self.send_message(message)
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get task status"""
        return self.tasks.get(task_id)
    
    async def process_task_result(self, task_id: str, result: str, agent_id: str):
        """Process completed task result"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.assigned_agent = agent_id
            task.completed_at = datetime.now()
    
    async def process_task_error(self, task_id: str, error: str, agent_id: str):
        """Process task error"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = TaskStatus.FAILED
            task.result = f"Error: {error}"
            task.assigned_agent = agent_id
            task.completed_at = datetime.now()

# Global agent manager
agent_manager = AgentManager()

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await agent_manager.initialize_agents()
    logger.info("Web Search Agent System started")
    yield
    # Shutdown
    logger.info("Shutting down agents")

# FastAPI App
app = FastAPI(
    title="AI Web Search Agent System",
    description="Two-agent system for intelligent web search with source validation",
    version="2.0.0",
    lifespan=lifespan
)

# Routes
@app.get("/")
async def root():
    return {
        "message": "AI Web Search Agent System",
        "status": "running",
        "agents": list(agent_manager.agents.keys()),
        "active_tasks": len([t for t in agent_manager.tasks.values() if t.status == TaskStatus.PROCESSING]),
        "capabilities": ["web_search", "source_validation", "comprehensive_research"]
    }

@app.post("/search", response_model=TaskResponse)
async def search_query(task_request: TaskRequest):
    """Submit a search query for research"""
    try:
        task_id = await agent_manager.create_task(
            task_request.description,
            "research"
        )
        
        return TaskResponse(
            task_id=task_id,
            status="pending",
            assigned_agent=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/{task_id}", response_model=TaskResponse)
async def get_search_result(task_id: str):
    """Get search result with sources"""
    task = await agent_manager.get_task_status(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Search task not found")
    
    # Extract sources from result if available
    sources = []
    if task.result and task.status == TaskStatus.COMPLETED:
        # Parse sources from the formatted result
        # In production, you might want to store sources separately
        pass
    
    return TaskResponse(
        task_id=task.id,
        status=task.status.value,
        result=task.result,
        assigned_agent=task.assigned_agent,
        sources=sources
    )

@app.get("/tasks")
async def list_tasks():
    """List all search tasks"""
    return {
        "tasks": [
            {
                "id": task.id,
                "description": task.description,
                "status": task.status.value,
                "assigned_agent": task.assigned_agent,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "has_result": bool(task.result)
            }
            for task in agent_manager.tasks.values()
        ]
    }

@app.get("/agents")
async def list_agents():
    """List all agents and their capabilities"""
    return {
        "agents": [
            {
                "id": agent.agent_id,
                "type": agent.agent_type.value,
                "capabilities": agent.capabilities,
                "is_busy": agent.is_busy
            }
            for agent in agent_manager.agents.values()
        ]
    }

@app.post("/tasks/{task_id}/retry")
async def retry_search(task_id: str):
    """Retry a failed search task"""
    task = await agent_manager.get_task_status(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status == TaskStatus.COMPLETED:
        return {"message": "Task already completed", "result": task.result}
    
    # Reset task status and resend to coordinator
    task.status = TaskStatus.PENDING
    task.assigned_agent = None
    task.result = None
    task.completed_at = None
    
    message = Message(
        id=str(uuid.uuid4()),
        sender="system",
        receiver="coordinator",
        content=json.dumps({
            "task_id": task_id,
            "description": task.description,
            "task_type": "research"
        }),
        timestamp=datetime.now(),
        message_type="task_request"
    )
    
    await agent_manager.send_message(message)
    return {"message": "Search retry initiated", "task_id": task_id}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agents_count": len(agent_manager.agents),
        "active_searches": len([t for t in agent_manager.tasks.values() if t.status == TaskStatus.PROCESSING]),
        "total_searches": len(agent_manager.tasks),
        "message_history_size": len(agent_manager.message_history),
        "system_info": {
            "coordinator_active": "coordinator" in agent_manager.agents,
            "researcher_active": "researcher" in agent_manager.agents
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
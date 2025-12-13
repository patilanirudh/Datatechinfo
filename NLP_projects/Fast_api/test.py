from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx
from typing import Dict, List, Optional, Any
import asyncio
import json
import uuid
from datetime import datetime
from enum import Enum
import logging
from contextlib import asynccontextmanager

import os
from dataclasses import dataclass, asdict

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
    WRITER = "writer"
    ANALYZER = "analyzer"

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

class TaskRequest(BaseModel):
    description: str
    task_type: str = "general"
    priority: int = 1

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[str] = None
    assigned_agent: Optional[str] = None

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

# Specific Agent Implementations
class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("coordinator", AgentType.COORDINATOR)
        self.capabilities = ["task_distribution", "coordination", "planning"]
        self.agent_registry = {}
    
    async def process_message(self, message: Message) -> Optional[Message]:
        logger.info(f"Coordinator processing: {message.content}")
        
        if message.message_type == "task_request":
            return await self.distribute_task(message)
        elif message.message_type == "task_result":
            return await self.handle_task_result(message)
        
        return None
    
    async def distribute_task(self, message: Message) -> Message:
        """Distribute task to appropriate agent"""
        content = json.loads(message.content)
        task_type = content.get("task_type", "general")
        
        # Simple task routing logic
        if "research" in task_type.lower() or "find" in content.get("description", "").lower():
            target_agent = "researcher"
        elif "write" in task_type.lower() or "create" in content.get("description", "").lower():
            target_agent = "writer"
        elif "analyze" in task_type.lower() or "analyze" in content.get("description", "").lower():
            target_agent = "analyzer"
        else:
            target_agent = "writer"  # Default
        
        return Message(
            id=str(uuid.uuid4()),
            sender=self.agent_id,
            receiver=target_agent,
            content=message.content,
            timestamp=datetime.now(),
            message_type="task_assignment"
        )
    
    async def handle_task_result(self, message: Message) -> Optional[Message]:
        """Handle completed task results"""
        logger.info(f"Task completed by {message.sender}")
        return None
    
    async def execute_task(self, task: Task) -> str:
        return f"Task {task.id} coordinated and distributed"

class ResearcherAgent(BaseAgent):
    def __init__(self):
        super().__init__("researcher", AgentType.RESEARCHER)
        self.capabilities = ["web_search", "data_gathering", "fact_checking"]
    
    async def process_message(self, message: Message) -> Optional[Message]:
        if message.message_type == "task_assignment":
            content = json.loads(message.content)
            task_desc = content.get("description", "")
            
            # Simulate research work
            result = await self.conduct_research(task_desc)
            
            return Message(
                id=str(uuid.uuid4()),
                sender=self.agent_id,
                receiver="coordinator",
                content=json.dumps({"result": result, "task_id": content.get("task_id")}),
                timestamp=datetime.now(),
                message_type="task_result"
            )
        return None
    
    async def conduct_research(self, query: str) -> str:
        """Simulate research process"""
        await asyncio.sleep(1)  # Simulate work
        
        # Mock research results
        research_results = {
            "query": query,
            "findings": [
                "Research finding 1 related to the query",
                "Research finding 2 with additional context",
                "Research finding 3 with supporting evidence"
            ],
            "sources": ["Source 1", "Source 2", "Source 3"],
            "confidence": 0.85
        }
        
        return f"Research completed for: {query}\n\nFindings:\n" + \
               "\n".join([f"- {finding}" for finding in research_results["findings"]])
    
    async def execute_task(self, task: Task) -> str:
        return await self.conduct_research(task.description)

class WriterAgent(BaseAgent):
    def __init__(self):
        super().__init__("writer", AgentType.WRITER)
        self.capabilities = ["content_creation", "summarization", "formatting"]
    
    async def process_message(self, message: Message) -> Optional[Message]:
        if message.message_type == "task_assignment":
            content = json.loads(message.content)
            task_desc = content.get("description", "")
            
            result = await self.create_content(task_desc)
            
            return Message(
                id=str(uuid.uuid4()),
                sender=self.agent_id,
                receiver="coordinator",
                content=json.dumps({"result": result, "task_id": content.get("task_id")}),
                timestamp=datetime.now(),
                message_type="task_result"
            )
        return None
    
    async def create_content(self, prompt: str) -> str:
        """Create content based on prompt"""
        await asyncio.sleep(1)  # Simulate work
        
        return f"Content created for: {prompt}\n\n" + \
               "This is a comprehensive response that addresses the key points mentioned in the prompt. " + \
               "The content is well-structured and provides valuable information that meets the requirements."
    
    async def execute_task(self, task: Task) -> str:
        return await self.create_content(task.description)

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("analyzer", AgentType.ANALYZER)
        self.capabilities = ["data_analysis", "pattern_recognition", "insights"]
    
    async def process_message(self, message: Message) -> Optional[Message]:
        if message.message_type == "task_assignment":
            content = json.loads(message.content)
            task_desc = content.get("description", "")
            
            result = await self.analyze_data(task_desc)
            
            return Message(
                id=str(uuid.uuid4()),
                sender=self.agent_id,
                receiver="coordinator",
                content=json.dumps({"result": result, "task_id": content.get("task_id")}),
                timestamp=datetime.now(),
                message_type="task_result"
            )
        return None
    
    async def analyze_data(self, data_description: str) -> str:
        """Analyze data based on description"""
        await asyncio.sleep(1)  # Simulate work
        
        return f"Analysis completed for: {data_description}\n\n" + \
               "Key insights:\n" + \
               "- Pattern 1: Significant trend identified\n" + \
               "- Pattern 2: Correlation found between variables\n" + \
               "- Pattern 3: Anomaly detected requiring attention\n\n" + \
               "Recommendations based on analysis provided."
    
    async def execute_task(self, task: Task) -> str:
        return await self.analyze_data(task.description)

# Agent Manager
class AgentManager:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.message_history: List[Message] = []
        
    async def initialize_agents(self):
        """Initialize all agents"""
        agents = [
            CoordinatorAgent(),
            ResearcherAgent(),
            WriterAgent(),
            AnalyzerAgent()
        ]
        
        for agent in agents:
            self.agents[agent.agent_id] = agent
            asyncio.create_task(agent.start_listening())
        
        logger.info(f"Initialized {len(agents)} agents")
    
    async def send_message(self, message: Message):
        """Send message to target agent"""
        if message.receiver in self.agents:
            await self.agents[message.receiver].message_queue.put(message)
            self.message_history.append(message)
        else:
            logger.error(f"Agent {message.receiver} not found")
    
    async def create_task(self, description: str, task_type: str = "general") -> str:
        """Create new task"""
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

# Global agent manager
agent_manager = AgentManager()

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await agent_manager.initialize_agents()
    yield
    # Shutdown
    logger.info("Shutting down agents")

# FastAPI App
app = FastAPI(
    title="Agentic AI System",
    description="A production-ready FastAPI application with AI agents",
    version="1.0.0",
    lifespan=lifespan
)

# Routes
@app.get("/")
async def root():
    return {
        "message": "Agentic AI System",
        "status": "running",
        "agents": list(agent_manager.agents.keys()),
        "active_tasks": len([t for t in agent_manager.tasks.values() if t.status == TaskStatus.PROCESSING])
    }

@app.post("/tasks", response_model=TaskResponse)
async def create_task(task_request: TaskRequest):
    """Create a new task"""
    try:
        task_id = await agent_manager.create_task(
            task_request.description,
            task_request.task_type
        )
        
        return TaskResponse(
            task_id=task_id,
            status="pending",
            assigned_agent=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task status and result"""
    task = await agent_manager.get_task_status(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        task_id=task.id,
        status=task.status.value,
        result=task.result,
        assigned_agent=task.assigned_agent
    )

@app.get("/tasks")
async def list_tasks():
    """List all tasks"""
    return {
        "tasks": [
            {
                "id": task.id,
                "description": task.description,
                "status": task.status.value,
                "assigned_agent": task.assigned_agent,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            for task in agent_manager.tasks.values()
        ]
    }

@app.get("/agents")
async def list_agents():
    """List all agents"""
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

@app.get("/messages")
async def get_messages():
    """Get message history"""
    return {
        "messages": [
            {
                "id": msg.id,
                "sender": msg.sender,
                "receiver": msg.receiver,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "message_type": msg.message_type
            }
            for msg in agent_manager.message_history[-50:]  # Last 50 messages
        ]
    }

@app.post("/agents/{agent_id}/direct")
async def send_direct_message(agent_id: str, message: dict):
    """Send direct message to specific agent"""
    if agent_id not in agent_manager.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    msg = Message(
        id=str(uuid.uuid4()),
        sender="user",
        receiver=agent_id,
        content=json.dumps(message),
        timestamp=datetime.now(),
        message_type="direct_message"
    )
    
    await agent_manager.send_message(msg)
    return {"status": "message_sent", "message_id": msg.id}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agents_count": len(agent_manager.agents),
        "active_tasks": len([t for t in agent_manager.tasks.values() if t.status == TaskStatus.PROCESSING]),
        "total_tasks": len(agent_manager.tasks),
        "message_history_size": len(agent_manager.message_history)
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
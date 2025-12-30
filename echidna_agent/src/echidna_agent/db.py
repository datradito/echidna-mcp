import psycopg
from psycopg import AsyncConnection
from .config import settings
import asyncio

async def get_db_connection() -> AsyncConnection:
    return await psycopg.AsyncConnection.connect(settings.ECHIDNA_AGENT_DB_URL)

def init_db():
    """Initialize the database schema and tables."""
    print(f"Initializing database at {settings.ECHIDNA_AGENT_DB_URL}...")
    try:
        with psycopg.connect(settings.ECHIDNA_AGENT_DB_URL) as conn:
            with conn.cursor() as cur:
                # Create schema
                cur.execute("CREATE SCHEMA IF NOT EXISTS echidna_agents;")
                
                # Create agent_jobs table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS echidna_agents.agent_jobs (
                        job_id UUID PRIMARY KEY,
                        agent_name VARCHAR(50) NOT NULL,
                        status VARCHAR(20) NOT NULL, -- 'queued', 'running', 'completed', 'failed'
                        input_payload JSONB,
                        output_payload JSONB,
                        error_message JSONB, -- Structured error object
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """)
                
                # Create checkpoints table (for LangGraph)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS echidna_agents.checkpoints (
                        thread_id TEXT PRIMARY KEY,
                        checkpoint JSONB NOT NULL,
                        metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                        parent_checkpoint_id TEXT
                    );
                """)
                
                # Create writes table for LangGraph
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS echidna_agents.checkpoint_writes (
                        thread_id TEXT,
                        checkpoint_id TEXT,
                        task_id TEXT,
                        idx INTEGER,
                        channel TEXT,
                        type TEXT,
                        value JSONB,
                        PRIMARY KEY (thread_id, checkpoint_id, task_id, idx)
                    );
                """)
                
            conn.commit()
            print("Database initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        raise

if __name__ == "__main__":
    init_db()

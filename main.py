#!/usr/bin/env python3
"""
Adastrea Director - AI Game Director Assistant

Main CLI interface for interacting with the AI Game Director.
Provides context-aware question answering based on ingested project documents.

Usage:
    python main.py
    python main.py --collection-name my_project
"""

import os
import sys
import argparse
import time
import copy
from typing import List, Dict, Any, Optional
from exceptions import (
    APIKeyError,
    DatabaseError,
    NetworkError,
    EmptyDatabaseError,
)

# Disable ChromaDB telemetry BEFORE any imports that might import chromadb
# This prevents "capture() takes 1 positional argument but 3 were given" errors
os.environ["ANONYMIZED_TELEMETRY"] = "False"

# Force UTF-8 encoding for stdout/stderr to handle Unicode characters (emojis)
# This prevents encoding errors on Windows systems with cp1252 encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from dotenv import load_dotenv
    # Load environment variables immediately after import
    load_dotenv()
    
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory
    from langchain.prompts import PromptTemplate
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich import print as rprint
except ImportError as e:
    print(f"Error: Missing required dependencies. Please install requirements.txt")
    print(f"Details: {e}")
    print(f"\nTo install dependencies, run:")
    print(f"  pip install -r requirements.txt")
    print(f"\nOr use the setup script:")
    print(f"  ./setup.sh")
    sys.exit(1)

console = Console(legacy_windows=False)


class QueryAgent:
    """Agent responsible for processing user queries and generating responses."""

    def __init__(
        self,
        collection_name: str = "adastrea_docs",
        persist_directory: str = "./chroma_db",
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        search_type: str = "mmr",
        retrieval_k: int = 6,
        fetch_k: int = 20,
    ):
        """
        Initialize the query agent.

        Args:
            collection_name: Name of the collection in the vector database
            persist_directory: Directory where vector database is stored
            model_name: Name of the OpenAI model to use
            temperature: Temperature for response generation (0-1)
            search_type: Type of search to use ("similarity" or "mmr")
            retrieval_k: Number of documents to retrieve (default: 6)
            fetch_k: Number of documents to fetch before MMR reranking (default: 20)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.model_name = model_name
        self.temperature = temperature
        # Validate parameters
        if retrieval_k <= 0:
            raise ValueError("retrieval_k must be greater than 0")
        if fetch_k <= 0:
            raise ValueError("fetch_k must be greater than 0")
        if search_type == "mmr" and fetch_k < retrieval_k:
            raise ValueError("fetch_k must be >= retrieval_k when using MMR search")
        
        self.search_type = search_type
        self.retrieval_k = retrieval_k
        self.fetch_k = fetch_k
        
        # Simple in-memory cache for query results (FIFO eviction, max 50 entries)
        self.query_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_max_size = 50

        # Initialize components
        self._initialize_components()

    def _initialize_components(self):
        """Initialize LLM, embeddings, vector store, and conversation chain."""
        try:
            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings()

            # Load vector store
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )

            # Check if database has documents
            if self.vectorstore._collection.count() == 0:
                error = EmptyDatabaseError(self.collection_name)
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
                sys.exit(1)

            # Initialize LLM
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=self.temperature,
            )

            # Initialize memory for conversation history
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer",
            )

            # Create custom prompt template
            prompt_template = """You are the Adastrea Director, an AI assistant specialized in helping with game development in Unreal Engine. You have access to project documentation, code, and design documents.

Use the following pieces of context to answer the question. If you don't know the answer based on the provided context, say so - don't make up information.

When answering:
- Be concise but thorough
- Reference specific documents or sections when relevant
- Provide actionable advice when appropriate
- Use technical terminology correctly
- If the question is about implementation, suggest practical approaches

Context: {context}

Question: {question}

Answer:"""

            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"],
            )

            # Create conversational retrieval chain with optimized retrieval
            search_kwargs = {"k": self.retrieval_k}
            if self.search_type == "mmr":
                # Use MMR (Maximal Marginal Relevance) for better diversity
                search_kwargs["fetch_k"] = self.fetch_k
            
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.vectorstore.as_retriever(
                    search_type=self.search_type,
                    search_kwargs=search_kwargs
                ),
                memory=self.memory,
                return_source_documents=True,
                combine_docs_chain_kwargs={"prompt": PROMPT},
            )

            console.print("[green]✓ AI Assistant initialized successfully[/green]")

        except EmptyDatabaseError:
            # Re-raise to handle at call site
            raise
        except Exception as e:
            error_msg = str(e).lower()
            
            if "api" in error_msg and "key" in error_msg:
                error = APIKeyError("OpenAI", str(e))
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            elif any(word in error_msg for word in ["connection", "network", "timeout"]):
                error = NetworkError("initialization", str(e))
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            elif any(word in error_msg for word in ["chroma", "database", "persist"]):
                error = DatabaseError("initialization", str(e))
                console.print(f"[red]{error.message}[/red]")
                console.print(f"[yellow]{error.details}[/yellow]")
            else:
                console.print(f"[red]Error initializing agent: {e}[/red]")
                console.print(f"[yellow]Check your configuration and try again[/yellow]")
            
            sys.exit(1)

    def _get_query_hash(self, query: str) -> str:
        """
        Generate a hash for query caching.
        Uses Python's built-in hash() for fast, non-cryptographic cache key generation.
        """
        return str(hash(query.lower().strip()))
    
    def process_query(self, query: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Process a user query and generate a response.

        Args:
            query: User's question
            use_cache: Whether to use cached results for identical queries

        Returns:
            Dictionary containing answer, source documents, and processing time
        """
        try:
            start_time = time.time()
            
            # Check cache for identical query
            query_hash = self._get_query_hash(query)
            if use_cache and query_hash in self.query_cache:
                cached_result = copy.deepcopy(self.query_cache[query_hash])
                cached_result["cached"] = True
                cached_result["processing_time"] = time.time() - start_time
                return cached_result
            
            result = self.qa_chain({"question": query})
            processing_time = time.time() - start_time
            
            # Add performance metrics to result
            result["processing_time"] = processing_time
            result["cached"] = False
            
            # Cache the result (FIFO eviction: remove oldest inserted entry if full)
            if use_cache:
                if len(self.query_cache) >= self.cache_max_size:
                    # Remove oldest inserted entry (first item in insertion order)
                    self.query_cache.pop(next(iter(self.query_cache)))
                self.query_cache[query_hash] = copy.deepcopy(result)
            
            return result
        except TimeoutError as e:
            error = NetworkError("query processing",
                "The request timed out. The API may be experiencing high load. "
                "Try again in a few moments."
            )
            console.print(f"[red]{error.message}[/red]")
            console.print(f"[yellow]{error.details}[/yellow]")
            return {
                "answer": "I encountered a timeout error. Please try again in a moment.",
                "source_documents": [],
            }
        except Exception as e:
            error_msg = str(e).lower()
            
            # Provide specific error messages based on error type
            if "rate" in error_msg and "limit" in error_msg:
                return {
                    "answer": "Rate limit exceeded. Please wait a few moments before asking another question.",
                    "source_documents": [],
                }
            elif "api" in error_msg and "key" in error_msg:
                return {
                    "answer": "API key error. Please check your OpenAI API key configuration.",
                    "source_documents": [],
                }
            elif any(word in error_msg for word in ["connection", "network"]):
                return {
                    "answer": "Network error. Please check your internet connection and try again.",
                    "source_documents": [],
                }
            else:
                console.print(f"[red]Error processing query: {e}[/red]")
                return {
                    "answer": "I encountered an error processing your query. Please try again.",
                    "source_documents": [],
                }

    def get_database_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded database.

        Returns:
            Dictionary with database information
        """
        try:
            count = self.vectorstore._collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory,
            }
        except Exception as e:
            console.print(f"[yellow]Could not retrieve database info: {e}[/yellow]")
            return {}


class AdastreaDirectorCLI:
    """Command-line interface for the Adastrea Director."""

    def __init__(self, agent: QueryAgent):
        """
        Initialize the CLI.

        Args:
            agent: QueryAgent instance
        """
        self.agent = agent
        self.running = True

    def print_banner(self):
        """Print the application banner."""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🤖 ADASTREA DIRECTOR                         ║
║          AI Game Development Assistant                    ║
║                                                           ║
║              Phase 1: Context-Aware Assistant             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """
        console.print(banner, style="bold cyan")

    def print_help(self):
        """Print help information."""
        help_text = """
**Available Commands:**

• Type your question and press Enter to ask the AI
• `help` - Show this help message
• `info` - Display database information
• `clear` - Clear conversation history
• `quit` or `exit` - Exit the assistant

**Example Questions:**

• "What is the main gameplay loop?"
• "Describe the player character abilities"
• "What are the performance requirements?"
• "How should I implement the quantum phase shift mechanic?"
• "What game systems need to be created?"

**Tips:**

• Ask follow-up questions - the AI remembers the conversation
• Be specific for better answers
• Reference documents by name when needed
        """
        console.print(Panel(Markdown(help_text), title="Help", border_style="cyan"))

    def print_database_info(self):
        """Print information about the loaded database."""
        info = self.agent.get_database_info()
        if info:
            info_text = f"""
**Database Information:**

• Collection: `{info['collection_name']}`
• Documents: `{info['document_count']}` chunks
• Location: `{info['persist_directory']}`
            """
            console.print(
                Panel(Markdown(info_text), title="Database Info", border_style="cyan")
            )

    def clear_conversation(self):
        """Clear the conversation history."""
        self.agent.memory.clear()
        console.print("[green]✓ Conversation history cleared[/green]")

    def process_command(self, user_input: str) -> bool:
        """
        Process a user command.

        Args:
            user_input: User's input

        Returns:
            True if should continue, False if should exit
        """
        command = user_input.lower().strip()

        if command in ["quit", "exit", "q"]:
            console.print("\n[cyan]Thank you for using Adastrea Director. Goodbye![/cyan]\n")
            return False

        elif command == "help":
            self.print_help()

        elif command == "info":
            self.print_database_info()

        elif command == "clear":
            self.clear_conversation()

        else:
            # Process as query
            with console.status("[cyan]Thinking...[/cyan]", spinner="dots"):
                result = self.agent.process_query(user_input)

            # Display answer
            console.print("\n[bold cyan]Answer:[/bold cyan]")
            console.print(Markdown(result["answer"]))

            # Display source documents if available
            if result.get("source_documents"):
                console.print(
                    f"\n[dim]Based on {len(result['source_documents'])} document(s)[/dim]"
                )
            
            # Display performance metrics
            if result.get("processing_time"):
                cached_indicator = " (cached)" if result.get("cached") else ""
                console.print(
                    f"[dim]Response time: {result['processing_time']:.2f}s{cached_indicator}[/dim]"
                )

            console.print()  # Empty line for spacing

        return True

    def run(self):
        """Run the interactive CLI."""
        self.print_banner()

        # Show initial info
        self.print_database_info()
        console.print("\n[cyan]Type 'help' for available commands or ask a question to get started.[/cyan]\n")

        # Main loop
        while self.running:
            try:
                # Get user input
                user_input = console.input("[bold green]You:[/bold green] ").strip()

                if not user_input:
                    continue

                # Process input
                self.running = self.process_command(user_input)

            except KeyboardInterrupt:
                console.print(
                    "\n\n[cyan]Interrupted. Type 'quit' to exit or press Ctrl+C again.[/cyan]\n"
                )
                try:
                    # Give user a chance to type quit
                    user_input = console.input(
                        "[bold green]You:[/bold green] "
                    ).strip()
                    if user_input.lower() in ["quit", "exit", "q"]:
                        self.running = False
                except KeyboardInterrupt:
                    console.print(
                        "\n[cyan]Goodbye![/cyan]\n"
                    )
                    self.running = False

            except EOFError:
                console.print("\n[cyan]Goodbye![/cyan]\n")
                self.running = False

            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]\n")


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Adastrea Director - AI Game Development Assistant"
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="adastrea_docs",
        help="Name of the document collection (default: adastrea_docs)",
    )
    parser.add_argument(
        "--persist-dir",
        type=str,
        default="./chroma_db",
        help="Directory where database is stored (default: ./chroma_db)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-3.5-turbo",
        help="OpenAI model to use (default: gpt-3.5-turbo)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature for response generation (default: 0.7)",
    )
    parser.add_argument(
        "--search-type",
        type=str,
        default="mmr",
        choices=["similarity", "mmr"],
        help="Search type: 'similarity' for basic similarity search, 'mmr' for diverse results (default: mmr)",
    )
    parser.add_argument(
        "--retrieval-k",
        type=int,
        default=6,
        help="Number of documents to retrieve (default: 6)",
    )
    parser.add_argument(
        "--fetch-k",
        type=int,
        default=20,
        help="Number of documents to fetch before MMR reranking (only used with --search-type mmr, default: 20)",
    )

    args = parser.parse_args()
    
    # Validate arguments
    if args.retrieval_k <= 0:
        parser.error("--retrieval-k must be greater than 0")
    if args.fetch_k <= 0:
        parser.error("--fetch-k must be greater than 0")
    if args.search_type == "mmr" and args.fetch_k < args.retrieval_k:
        parser.error("--fetch-k must be >= --retrieval-k when using MMR search")

    # Initialize agent
    agent = QueryAgent(
        collection_name=args.collection_name,
        persist_directory=args.persist_dir,
        model_name=args.model,
        temperature=args.temperature,
        search_type=args.search_type,
        retrieval_k=args.retrieval_k,
        fetch_k=args.fetch_k,
    )

    # Run CLI
    cli = AdastreaDirectorCLI(agent)
    cli.run()


if __name__ == "__main__":
    main()

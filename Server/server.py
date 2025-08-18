from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from llm.llm import LLM
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os

from elevenlabs.client import ElevenLabs
from contextlib import asynccontextmanager
from routes.admin import admin_router
from routes.user import user_router

#########################################################################
#                               Server.py
#
#   Contents:
#   - FastAPI Server for AI Chatbot
#   - RESTful API endpoints for managing the chatbot
#   - Real-time voice interaction via WebSockets
#
#########################################################################

########################################### REQUEST STRUCTURE #######################################

class InitRequest(BaseModel):
    index_name: str = "default"

class ChatRequest(BaseModel):
    prompt: str

class QueryRequest(BaseModel):
    query: str
    k: int = 5

class AddDataRequest(BaseModel):
    text_array: List[str]

class ScrapRequest(BaseModel):
    url: str

class PromptRequest(BaseModel):
    prompt: str

class ResetPromptRequest(BaseModel):
    pass

class VoiceAssistant(BaseModel):
    pass

########################################################################################################
#
#    Encapsulates the FastAPI server, implementing a singleton pattern to ensure only one
#    instance of the server and its resources (like the LLM) exist.
#
########################################################################################################

class Server:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Server, cls).__new__(cls)
        return cls._instance

    def __init__(self):

        self.llm_instance: Optional[LLM] = None
        self.current_index: Optional[str] = None
        self.eleven_client = ElevenLabs()

        self.app = FastAPI(
            title="AI ChatBot API",
            description="A modern AI chatbot powered by Google Gemini and Pinecone",
            version="1.0.0",
            lifespan=self.lifespan,
        )
        self.app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
        self._setupRoutes()
        self._setupFrontend()

    @staticmethod
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup Code
        logo = r"""
             ██████╗██╗  ██╗ █████╗ ████████╗    ██████╗  ██████╗ ████████╗
            ██╔════╝██║  ██║██╔══██╗╚══██╔══╝    ██╔══██╗██╔═══██╗╚══██╔══╝
            ██║     ███████║███████║   ██║       ██████╔╝██║   ██║   ██║   
            ██║     ██╔══██║██╔══██║   ██║       ██╔══██╗██║   ██║   ██║   
            ╚██████╗██║  ██║██║  ██║   ██║       ██████╔╝╚██████╔╝   ██║   
             ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═════╝  ╚═════╝    ╚═╝   
             """
        print(logo)
        yield 
        print("🛑 AI ChatBot API shutting down...")

    ##################################################################################
    #                            ROUTE SETUP
    ##################################################################################
    def _setupRoutes(self):
        self.app.include_router(admin_router,prefix='/api')
        self.app.include_router(user_router,prefix='/api')

    def _setupFrontend(self) -> None:
        # Serve React build if present, without interfering with /api routes
        dist_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Frontend", "dist"))
        index_file = os.path.join(dist_root, "index.html")
        assets_dir = os.path.join(dist_root, "assets")

        if os.path.exists(index_file):
            if os.path.isdir(assets_dir):
                self.app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

            @self.app.get("/", include_in_schema=False)
            async def serve_index_root():
                return FileResponse(index_file)

            # SPA fallback: any non-API path returns index.html
            @self.app.get("/{full_path:path}", include_in_schema=False)
            async def spa_fallback(full_path: str):
                if full_path.startswith("api"):
                    return FileResponse(index_file, status_code=404)
                return FileResponse(index_file)


    def get_app(self) -> FastAPI:
        return self.app

# Create the singleton server instance and get the app
server = Server()
app = server.get_app()

if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = "0.0.0.0"
    url = f"http://localhost:{port}"

    print(f"\n🚀 Starting server at: {url}\n")

    uvicorn.run("server:app", host=host, port=port)
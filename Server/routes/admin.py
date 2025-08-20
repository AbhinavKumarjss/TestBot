import traceback
from typing import List
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from httpx import request
from pydantic import BaseModel

from llm.llm import LLM
from pc.pinecone import PineconeClient
from utils.webscrapper.webscrapper import scrape_page_and_its_links
from prompts import get_chat_prompt,get_voice_prompt,set_chat_prompt,set_voice_prompt,reset_chat_prompt,reset_voice_prompt
admin_router = APIRouter(prefix="/admin",tags=['Admin'])
llm = LLM()
pc = PineconeClient()

################################################################################################
#                                           Request Structure
################################################################################################

class ScrapeRequest(BaseModel):
    url : str
    limit: int

class PineconeSetIndexRequest(BaseModel):
    indexName: str = "default"

class PineconeQueryIndexRequest(BaseModel):
    query: str 
    top:int

class PineconeDataAddRequest(BaseModel):
    textarray:List[str]

class SetPromptRequest(BaseModel):
    systemprompt: str
################################################################################################
#                                           Admin Routes 
################################################################################################

@admin_router.get('/dashboard')
async def dashboard():
    return

############################### PINECONE ###########################

@admin_router.post('/pinecone/index/change')
async def pineconeChangeIndex(request:PineconeSetIndexRequest):
    try:
        success , hasCreated = pc.switch_index(request.indexName)
        return JSONResponse({"success":success,"created":hasCreated})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

@admin_router.get('/pinecone/index/get')
async def pineconeGetIndex():
    try:
        return JSONResponse({"name":pc.getIndexName()})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

@admin_router.get('/pinecone/index/delete')
async def pineconeDeleteIndex():
    try:
        return JSONResponse({"success":pc.delete_index()})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

@admin_router.post('/pinecone/data/query')
async def pineconeDataQuery(request : PineconeQueryIndexRequest):
    try:
        return pc.query_index(request.query,request.top)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

@admin_router.post('/pinecone/data/add')
async def pineconeDataAdd(request : PineconeDataAddRequest):
    try:
        return  JSONResponse({"success" : pc.add_data_to_index(request.textarray)})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

############################### PROMPT REQUEST ##########################

@admin_router.post('/prompt/chat/set')
async def SetChatPrompt(request:SetPromptRequest):
    try:
        return set_chat_prompt(request.systemprompt)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

@admin_router.get('/prompt/chat/get')
async def GetChatPrompt():
    try:
        return JSONResponse({"prompt":get_chat_prompt()})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

@admin_router.get('/prompt/chat/reset')
async def ResetChatPrompt():
    try:
        return JSONResponse({"success" : reset_chat_prompt()})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

@admin_router.post('/prompt/voice/set')
async def SetVoicePrompt(request:SetPromptRequest):
    try:
        return set_voice_prompt(request.systemprompt)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

@admin_router.get('/prompt/voice/get')
async def GetVoicePrompt():
    try:
        return JSONResponse({"prompt":get_voice_prompt()})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)

@admin_router.get('/prompt/voice/reset')
async def ResetVoicePrompt():
    try:
        return JSONResponse({"success" : reset_voice_prompt()})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"success": False, "message": str(e)}, status_code=500)


########################################################
#               Web Scrapping Route (admin)
#
########################################################
@admin_router.post('/scrape/website')
async def scrap_url(request: ScrapeRequest):

    url = request.url
    link_limit = request.limit

    try:
        text = scrape_page_and_its_links(url, link_limit)

        # ✅ Print summary
        print(f"\n✅ Scraped {len(text)} chunks from {url}")
        print("-" * 50)

        # ✅ Print first 3 chunks for inspection
        for i, chunk in enumerate(text[:3]):
            print(f"🔹 Chunk {i + 1}/{len(text)} from URL: {chunk['source_url']}")
            print(f"🔢 Index: {chunk['chunk_index'] + 1}/{chunk['total_chunks']}")
            print(f"📏 Characters: {chunk['char_count']}")
            print("🧩 Content Preview:")
            print(chunk['content'][:300].strip() + "...")
            print("-" * 50)
            
        pc.add_scrape_data(text)
        return {"success": True, "text": text}
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"success": False, "message": f"Error scraping URL: {str(e)}"}, status_code=500)


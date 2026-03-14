# Main task : Create AI web scraping tool


import http.client
import json
import os
import httpx
import asyncio
from dotenv import load_dotenv
from fastmcp import FastMCP
from MapMyCode_tool.utils import clean_html_to_txt

load_dotenv(override=True)

mcp = FastMCP("docs")

# Step 1 : Search the web

SERPER_URL = "https://google.serper.dev/search"

async def search_web(query : str) -> dict | None:
    payload = json.dumps({"q": query , "num" : 2})
    headers = {
    'X-API-KEY': os.getenv("SERPER_API_KEY"),
    'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client: 
        response = await client.post(
            SERPER_URL, headers = headers, data = payload, timeout = 30.0
        )
        response.raise_for_status()
        return response.json()


async def fetch_url(url : str):
    async with httpx.AsyncClient() as client: 
        response = await client.get(url, timeout = 30.0)
        #parse and clean data
        cleaned_response = clean_html_to_txt(response.text)
        return cleaned_response

# Step 3 : Read documentation and write code accordingly

docs_urls = {
    "langchain": "docs.langchain.com",
    "llama-index": "docs.llamaindex.ai/en/stable",
    "openai": "platform.openai.com/docs",
    "uv": "docs.astral.sh/uv",
    "claude" : "platform.claude.com/docs",
    "groq" : "console.groq.com/docs/overview"
}

@mcp.tool()
async def get_docs(query : str, library : str):

    """
    Search the latest docs for a given query and library.
    Supports langchain, openai, llama-index and uv.

    Args:
        query : The query to search for (e.g. "Publish a package with UV")
        library : The library to search in (e.g. "uv")
    
    Returns : 
        Summarized text from the docs with source links.

    """
    
    if library not in docs_urls:
        raise ValueError(f"Library {library} not supported by this tool")
    
    search_query = f"site:{docs_urls[library]} {query}"

    results = await search_web(search_query)

    if len(results['organic']) == 0:
        return "No results found"
    
    text_parts = []
    for result in results['organic']:
        link = result.get('link',"")

        raw = await fetch_url(link)
        if raw:
            labeled = f"SOURCE : {link}\n{raw}"
            text_parts.append(labeled)
             
    return "\n\n".join(text_parts)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

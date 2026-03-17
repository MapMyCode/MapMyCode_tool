# Documentation for the **Map‑My‑Code** (MCP) Prototype  

*Version inferred from repository metadata – March 2026*  

---

## 1. Overall Codebase Objective  

| Aspect | Description |
|--------|-------------|
| **Purpose** | Provide a lightweight, command‑line‑driven “tool server” that can retrieve, clean, and surface documentation for a given Python library (or any searchable web site) and optionally let a Large Language Model (LLM) summarise or answer questions based on that material. |
| **Problem it solves** | Developers often need to look up library reference material quickly while coding. Manually opening a browser, copying snippets, and pasting them into an LLM is tedious. This project automates the search‑fetch‑clean pipeline and offers a standardized RPC‑style interface (FastMCP) that can be consumed by downstream tools or agents. |
| **Workflow / Application type** | 1. **Tool server** (`mcp_server.py`) runs under the FastMCP framework. <br>2. A client (e.g., an AI‑agent or a CLI) invokes the `get_docs` tool with a *query* and a *library* name. <br>3. The server uses the **SERPER** web‑search API to locate relevant pages on the library’s documentation site. <br>4. Each result is fetched with **httpx**, stripped of HTML noise via **trafilatura**, and concatenated into a plain‑text payload. <br>5. (Optional) The payload can be sent to a **Groq** LLM using the helper functions in `groq_call.py` or `MCP/utils.py` to produce a concise answer. |
| **Major capabilities (as inferred from file structure)** | - Environment‑aware configuration (`dotenv`). <br>- Asynchronous HTTP interactions (`httpx`). <br>- HTML‑to‑text extraction (`trafilatura`). <br>- LLM integration via Groq’s chat‑completion endpoint. <br>- Simple RPC server (`FastMCP`) exposing the `get_docs` tool. |

---

## 2. Logical Flow  

Below is a **reasoned end‑to‑end execution pipeline** based on the provided metadata. Wherever the exact detail is not explicit, the inference is marked.

1. **Startup** – The entry point is the `main()` function in `MCP/mcp_server.py`.  
   ```python
   def main():
       mcp.run(transport="stdio")   # launches the FastMCP server
   ```
   This starts a FastMCP process that listens on standard I/O (or any transport configured by the client).

2. **Tool Invocation** – A client sends a request to the server requesting the `get_docs` tool with two arguments: `query` (what the user wants to know) and `library` (the target documentation site, e.g., `pandas`).  

3. **Library Validation & Search Query Construction** – Inside `get_docs`, the code (inferred) checks the supplied `library` against a predefined map that links library names to their official docs domain. It then builds a *site‑restricted* SERPER query such as:  
   ```
   site:docs.pandas.org <user query>
   ```

4. **Web Search** – `search_web(query)` (async) sends a POST request to the **SERPER** API:  
   - Loads `SERPER_API_KEY` from the environment (via `dotenv`).  
   - Serialises the payload with `json.dumps`.  
   - Uses `httpx.AsyncClient` to post to the SERPER endpoint.  
   - Returns the parsed JSON response (list of organic results) or `None` on failure.

5. **Result Fetching & Cleaning** – For each organic result (up to a reasonable limit, inferred):  
   - `fetch_url(url)` performs an async `GET` with `httpx`.  
   - The raw HTML body is handed to `clean_html_to_txt(html)` (imported from `MCP/utils.py`).  
   - `clean_html_to_txt` calls `trafilatura.extract` with flags to strip comments, tables, etc., returning plain readable text or `None`.

6. **Aggregation** – The cleaned texts are prefixed with their source URL (e.g., `Source: https://pandas.pydata.org/...`) and concatenated with double newlines to form a single markdown‑friendly string that is returned to the caller.

7. **(Optional) LLM Summarisation** –  
   - The caller may subsequently invoke either `run_groq_api(prompt, model)` from `groq_call.py` **or** `get_response_from_llm(user_prompt, system_prompt, model)` from `MCP/utils.py`.  
   - Both helpers load the `GROQ_API_KEY`, instantiate a `groq.Groq` client, send a chat completion request with a fixed system message (or a custom one) and the user prompt, then return the first choice’s `content`.  
   - This step can be used to transform the raw documentation dump into a concise answer.

8. **Response Delivery** – The final string (raw docs or LLM‑generated summary) is sent back over the FastMCP transport to the original client.

> **Inference note:** The exact orchestration of LLM calls inside the server is not shown in the metadata. The presence of two similar helper modules (`groq_call.py` and `MCP/utils.py`) suggests that different entry points or experiments may choose either implementation.

---

## 3. File‑wise Explanations  

### `../groq_call.py`  

- **Purpose** – Provide a minimal, reusable wrapper around Groq’s chat‑completion API.  
- **Key Functions / Classes**  
  - `run_groq_api(prompt, model)` – Sends a user prompt (paired with a fixed system message) to Groq and returns the assistant’s response text.  
- **Role in Codebase** – Acts as a *utility* for any component that wishes to query a Groq LLM without dealing with environment handling or client boiler‑plate. It is especially handy for quick scripts or for the `MCP` server if it chooses this implementation for summarisation.  
- **Notes** –  
  - Loads `.env` via `dotenv.load_dotenv()` to obtain `GROQ_API_KEY`.  
  - Uses a **hard‑coded system prompt** (not exposed in metadata) which likely sets the LLM’s persona.  
  - Returns only the first choice, assuming `max_tokens` and other parameters are defaults.

---

### `../MCP/utils.py`  

- **Purpose** – Collection of helper utilities used by the MCP server: HTML cleaning and LLM interaction.  
- **Key Functions / Classes**  
  - `clean_html_to_txt(html)` – Converts raw HTML to plain, readable text using `trafilatura.extract`.  
  - `get_response_from_llm(user_prompt, system_prompt, model)` – Similar to `run_groq_api` but allows the caller to supply a custom system prompt, offering more flexibility.  
- **Role in Codebase** – Supplies the **core processing primitives** for the server:  
  - `clean_html_to_txt` is directly imported by `mcp_server.py` to tidy fetched pages.  
  - `get_response_from_llm` can be used wherever the project needs LLM‑generated output (e.g., summarising the concatenated docs).  
- **Notes** –  
  - Also loads environment variables (`dotenv`) to read the Groq API key.  
  - Returns `None` silently if HTML extraction fails (caller should handle the `None` case).  

---

### `../MCP/mcp_server.py`  

- **Purpose** – Define and launch the **FastMCP** tool server exposing the `get_docs` capability.  
- **Key Functions / Classes**  
  - `search_web(query)` – Async wrapper around the SERPER web‑search API.  
  - `fetch_url(url)` – Async downloader that retrieves a page and hands it to `clean_html_to_txt`.  
  - `get_docs(query, library)` – Orchestrates search → fetch → clean → aggregate, returning a single string with source‑annotated documentation snippets.  
  - `main()` – Starts the FastMCP server with a `stdio` transport.  
- **Role in Codebase** – The **entry point** and **public interface** of the project. It translates a high‑level request (`get_docs`) into concrete HTTP calls, processing, and (optionally) LLM interaction.  
- **Notes** –  
  - Relies on **environment variables**: `SERPER_API_KEY` for web search, and (indirectly via utils) `GROQ_API_KEY`.  
  - Uses **asynchronous I/O** (`httpx.AsyncClient`) to keep latency low when handling multiple URLs.  
  - The `FastMCP` library (not detailed in metadata) likely provides a simple RPC‑style framework; the server registers the `get_docs` tool automatically when `mcp.run()` is called.  

---

## 4. File‑wise Dependencies  

### `../groq_call.py`  

- **Depends on**:  
  - `os` – reads `GROQ_API_KEY` from environment.  
  - `dotenv.load_dotenv` – loads `.env` file at import time.  
  - `groq.Groq` – client class for communicating with the Groq API.  
- **Dependency purpose** – All three are external libraries; there are **no internal project imports**.  

---

### `../MCP/utils.py`  

- **Depends on**:  
  - `trafilatura` – provides `extract` for HTML‑to‑text conversion.  
  - `dotenv` – loads environment variables (Groq API key).  
  - `os` – accesses `GROQ_API_KEY`.  
  - `groq` – supplies the `Groq` client used in `get_response_from_llm`.  
- **Internal dependencies** – **None** (pure utility module).  

---

### `../MCP/mcp_server.py`  

- **Depends on**:  
  - `httpx` – asynchronous HTTP client for SERPER search and page fetches.  
  - `json` – serialises the SERPER request payload.  
  - `os` – reads `SERPER_API_KEY`.  
  - `dotenv` – loads the `.env` file at runtime.  
  - `fastmcp` – framework that creates the MCP server instance and registers tools.  
  - `MapMyCode_tool.MCP.utils` – imports `clean_html_to_txt` (used by `fetch_url`).  
- **Internal dependencies** –  
  - `MCP/utils.py` (via the qualified import path).  
- **Dependency purpose** –  
  - `httpx`, `json`, `os`, `dotenv` → external services & config handling.  
  - `fastmcp` → server orchestration.  
  - `MCP/utils` → HTML cleaning before aggregation.  

---

## 5. Summary for New Developers  

- **Start** by running `python -m MCP.mcp_server` (or invoking the `main` function) to launch the FastMCP server.  
- Ensure a `.env` file exists at the project root with two keys: `SERPER_API_KEY` (for web search) and `GROQ_API_KEY` (for LLM calls).  
- The primary public tool is `get_docs`. Call it through any FastMCP‑compatible client, providing a natural‑language query and the target library name.  
- If you need LLM summarisation, you can either:  
  1. Use `utils.get_response_from_llm` directly in your own script, or  
  2. Extend `mcp_server.py` to invoke `run_groq_api` after the documentation aggregation step.  
- The codebase is deliberately **modular**: web‑search, HTML cleaning, and LLM access live in separate modules, making it easy to swap out SERPER for another search provider, replace `trafilatura` with a different parser, or switch from Groq to another LLM vendor.  

---  

*End of documentation.*
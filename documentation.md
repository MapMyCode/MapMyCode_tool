# 📚 MapMyCode Tool – Architecture Overview  

*Version inferred from the repository structure: `MapMyCode_tool`*  

---  

## 1. Overall Codebase Objective  

| Aspect | Description |
|--------|-------------|
| **Purpose** | Provide a **micro‑service / command‑line assistant** that can query the web, fetch documentation pages, clean them to plain text, and pass the resulting material to a **Groq LLM** for further processing (e.g., answering questions, generating code diagrams, etc.). |
| **Problem it solves** | Developers often need quick, context‑aware answers that combine up‑to‑date web documentation with LLM reasoning. Manually copying/pasting docs into a chat model is tedious and error‑prone. This tool automates the retrieval‑clean‑query pipeline so the LLM receives high‑quality, relevant text. |
| **Workflow / Application type** | A **tool‑oriented server** (MCP – “Micro‑Component‑Protocol”) that runs over standard I/O (stdin/stdout) and exposes *tool functions* (e.g., `get_docs`) which can be invoked by an LLM‑driven agent. It also contains a lightweight helper (`groq_call.py`) for direct one‑off Groq API calls. |
| **Major capabilities** (as suggested by the file structure) | 1. **Groq LLM integration** – `run_groq_api` and `get_response_from_llm`. <br>2. **Web‑search via SERPER API** – asynchronous search of the public web. <br>3. **HTML → plain‑text extraction** – using `trafilatura`. <br>4. **MCP server** – registers the above utilities as *tools* that an LLM can call, and runs a REPL‑style server over stdio. |

---  

## 2. Logical Flow  

Below is a **reasoned end‑to‑end flow** based on the metadata. Where the exact order is not explicit, the inference is noted.

```
┌─────────────────────┐
│  Entry point        │
│  (mcp_server.main)  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  FastMCP server     │
│  (creates MCP app) │
│  registers tools    │
│  – get_docs          │
│  – (others could   │
│    be added)        │
└───────┬─────────────┘
        │
        ▼   (LLM invokes tool)
┌─────────────────────┐
│  get_docs(query,    │
│          library)   │
└───────┬─────────────┘
        │
        │ 1️⃣ Validate library → map of known doc sites
        │ 2️⃣ Build site‑restricted search term
        ▼
┌─────────────────────┐
│  search_web(query)  │  ← async HTTP POST to SERPER API
│  (returns JSON)     │
└───────┬─────────────┘
        │
        │  Iterate over `organic_results`
        ▼
┌─────────────────────┐
│  fetch_url(url)     │  ← async HTTP GET page HTML
│  → clean_html_to_txt│  (trafilatura) → plain text
└───────┬─────────────┘
        │
        │  Concatenate excerpts, prefix with source URL
        ▼
┌─────────────────────┐
│  Return assembled   │
│  documentation text│
└───────┬─────────────┘
        │
        │  (LLM receives the text, may call back
        │   Groq APIs via utils.get_response_from_llm
        │   or groq_call.run_groq_api)
        ▼
┌─────────────────────┐
│  LLM produces final│
│  answer / diagram  │
└─────────────────────┘
```

*Key points*  

* **Starting point** – The `main` function in `MCP/mcp_server.py`. It launches the MCP server with a *stdio* transport, making the tool usable from a terminal or as a subprocess of another program.  
* **Control flow** – An LLM (running elsewhere) sends a request to the MCP server to execute the `get_docs` tool. The tool internally performs a web search, fetches each result, cleans the HTML, and returns a consolidated plain‑text payload.  
* **LLM interaction** – The helper module `groq_call.py` (and `MCP/utils.py`’s `get_response_from_llm`) provide a thin wrapper around the Groq chat‑completion endpoint, allowing either the server or external scripts to query the LLM directly.  

---  

## 3. File‑wise Explanations  

### `groq_call.py`  

- **Purpose** – Minimal wrapper that sends a single user prompt to the Groq chat‑completion API and returns the assistant’s reply.  
- **Key Functions / Classes**  
  - `run_groq_api(prompt: str, model: str) -> str` – Builds a Groq client from the `GROQ_API_KEY` environment variable, posts a chat request containing a fixed system message and the user `prompt`, and extracts the text from the first response choice.  
- **Role in Codebase** – Acts as a **stand‑alone utility** for quick LLM calls (useful in scripts, notebooks, or debugging) without the extra context handling that `utils.get_response_from_llm` provides.  
- **Notes** –  
  - Relies on `.env` loading via `dotenv.load_dotenv()` (executed at import).  
  - The system prompt is hard‑coded; therefore the function is best for *single‑shot* interactions.  

---

### `MCP/utils.py`  

- **Purpose** – Collection of reusable helper functions used by the MCP server and possibly by external scripts.  
- **Key Functions / Classes**  
  - `clean_html_to_txt(html: str) -> Optional[str]` – Uses `trafilatura.extract` to strip HTML markup, comments, and tables, returning clean readable text.  
  - `get_response_from_llm(user_prompt: str, system_prompt: str, model: str) -> str` – Similar to `run_groq_api` but allows a custom system prompt and returns the LLM’s answer.  
- **Role in Codebase** – Provides **core LLM communication** and **HTML cleaning** utilities that are shared across the server (`mcp_server.py`) and could be imported elsewhere.  
- **Notes** –  
  - `dotenv.load_dotenv` is executed at import time, guaranteeing that `GROQ_API_KEY` is available for any function call.  
  - Error handling in `clean_html_to_txt` is defensive: returns `None` on extraction failure.  

---

### `MCP/mcp_server.py`  

- **Purpose** – Implements the **MCP (Micro‑Component‑Protocol) server** that exposes web‑search and documentation‑retrieval tools to an LLM.  
- **Key Functions / Classes**  
  - `search_web(query: str) -> Optional[dict]` – Sends an asynchronous POST request to the **SERPER** search API, returning the parsed JSON response (or `None` on failure).  
  - `fetch_url(url: str) -> Optional[str]` – Retrieves raw HTML of a URL via `httpx.AsyncClient`, then calls `clean_html_to_txt` to obtain plain text.  
  - `get_docs(query: str, library: str) -> str` – **MCP tool** (decorated with `@mcp.tool`) that: <br>1️⃣ Validates `library` against a pre‑defined map of documentation sites. <br>2️⃣ Performs a site‑restricted search, <br>3️⃣ Fetches each result, cleans it, and <br>4️⃣ Returns a concatenated, source‑annotated summary.  
  - `main()` – Entry point; runs the MCP server with `transport="stdio"` (standard input/output).  
- **Role in Codebase** – Serves as the **runtime façade**: it translates high‑level LLM tool calls into concrete web‑search, fetching, and cleaning operations, then streams the result back to the LLM.  
- **Notes** –  
  - Uses **asynchronous I/O** (`httpx.AsyncClient`) for efficiency when contacting multiple URLs.  
  - Environment variables (`SERPER_API_KEY`) are loaded at runtime via `dotenv.load_dotenv()`.  
  - The server is built on the external `fastmcp` library, which handles tool registration and I/O transport.  

---  

## 4. File‑wise Dependencies  

### `groq_call.py`  

- **Depends on**:  
  - `os` – reads `GROQ_API_KEY` from the environment.  
  - `dotenv` – `load_dotenv()` to populate environment variables from a `.env` file.  
  - `groq` – provides the `Groq` client class for API communication.  
- **Dependency purpose** – Access credentials (`os`), ensure they are loaded (`dotenv`), and perform the actual LLM request (`groq`).  
- **Remarks** – No internal project imports; completely self‑contained.

---

### `MCP/utils.py`  

- **Depends on**:  
  - `trafilatura` – `extract` function for HTML‑to‑text conversion.  
  - `os` – reads `GROQ_API_KEY`.  
  - `dotenv.load_dotenv` – loads environment variables at import time.  
  - `groq.Groq` – creates a client for Groq chat completions.  
- **Dependency purpose** –  
  - `trafilatura` supplies the core cleaning logic used by `clean_html_to_txt`.  
  - `os` & `dotenv` manage credentials.  
  - `groq` enables LLM interaction in `get_response_from_llm`.  
- **Remarks** – No imports from other project files; functions are reusable utilities.

---

### `MCP/mcp_server.py`  

- **Depends on** (internal & external):  
  - **External**:  
    - `httpx` – asynchronous HTTP client for SERPER calls and page fetching.  
    - `dotenv` – loads `.env` for `SERPER_API_KEY`.  
    - `fastmcp` – framework that creates the MCP server, registers tools, and runs the stdio transport.  
    - `json` – serializes the search payload.  
    - `os` – reads `SERPER_API_KEY`.  
  - **Internal**:  
    - `MapMyCode_tool.MCP.utils` – imports `clean_html_to_txt` (used inside `fetch_url`).  
- **Dependency purpose** –  
  - `httpx` provides non‑blocking network I/O for both search and page retrieval.  
  - `fastmcp` supplies the **tool‑exposure layer** (decorators, server runner).  
  - `dotenv` and `os` expose needed API keys.  
  - `json` builds the request body for SERPER.  
  - `utils.clean_html_to_txt` ensures fetched HTML is transformed into usable plain text before returning to the LLM.  
- **Remarks** – This file is the **central orchestrator**; it ties together web services, cleaning utilities, and the MCP framework.  

---  

### Summary of Internal Dependency Graph  

```
MCP/mcp_server.py
│
├─ imports → MCP/utils.py (clean_html_to_txt)
└─ (no other internal imports)
```

Both `groq_call.py` and `MCP/utils.py` are utility modules that can be used independently; they do **not** depend on the server module.

---  

## 5. Onboarding Checklist (for new developers)

1. **Set up environment**  
   - Create a `.env` file at the project root with:  
     ```dotenv
     GROQ_API_KEY=your_groq_key
     SERPER_API_KEY=your_serper_key
     ```  
   - Install required packages (as inferred from imports):  
     ```bash
     pip install python-dotenv groq trafilatura httpx fastmcp
     ```  

2. **Run the server**  
   ```bash
   python -m MapMyCode_tool.MCP.mcp_server
   # or, from the repository root:
   python MCP/mcp_server.py
   ```  
   The server will wait for tool calls over stdin/stdout.

3. **Call a tool** (example via a client script or an LLM agent)  
   ```json
   {
     "name": "get_docs",
     "arguments": {
       "query": "how to use pandas read_csv",
       "library": "pandas"
     }
   }
   ```  

4. **Use the low‑level Groq wrapper** (if you just need a quick LLM call):  
   ```python
   from MapMyCode_tool.groq_call import run_groq_api
   answer = run_groq_api("Explain the difference between list and tuple.", model="mixtral-8x7b-32768")
   print(answer)
   ```  

5. **Extend functionality**  
   - Add new `@mcp.tool` functions in `mcp_server.py` or separate modules.  
   - Re‑use `clean_html_to_txt` and `get_response_from_llm` from `MCP/utils.py` as needed.  

---  

*This documentation reflects the current metadata. If additional modules exist, expand the sections accordingly.*
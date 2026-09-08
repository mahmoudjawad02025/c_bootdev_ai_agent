> [!IMPORTANT]
> The folder structure could be enhanced, but it was kept as-is so checks on the Boot.dev site continue to pass safely.

# 🤖 Boot.dev AI Agent

CLI app that sends a user prompt to an LLM on [OpenRouter](https://openrouter.ai/). The model may request any of four local tools (list directory, read file, write file, run Python). Path arguments to those tools are checked against `./calculator`.

---

## 📑 Table of Contents

- [What it does](#-what-it-does)
- [Requirements](#-requirements)
- [Setup](#️-setup)
- [Usage](#-usage)
- [How it works](#-how-it-works)
- [Project layout](#-project-layout)

---

## ✨ What it does

- Takes one required prompt argument from the CLI (`argparse`), plus optional `--verbose`
- Uses the `openai` package with `base_url="https://openrouter.ai/api/v1"`, model `openrouter/free`, `temperature=0`
- Loops up to 20 times: call the API → if there are `tool_calls`, run them and append results → otherwise print the text reply and exit
- Sets `working_directory` to `"./calculator"` inside `call_function1` for every tool call
- Each tool returns an error string if the target path resolves outside that working directory
- On every tool call, prints the function name; with `--verbose`, prints name + arguments, prints each tool result, and on the final text reply also prints the user prompt and prompt/response token counts

---

## 📋 Requirements

- Python `>=3.14` (`pyproject.toml`); `.python-version` is `3.14`
- Env var `OPENROUTER_API_KEY` (app calls `load_dotenv()` then reads `os.environ`; missing key raises `RuntimeError`)

Dependencies listed in `pyproject.toml`: `openai==2.44.0`, `python-dotenv==1.1.0`.

---

## ⚙️ Setup

This repo has a `uv.lock`. Using [uv](https://github.com/astral-sh/uv):

```bash
git clone <your-repo-url>
cd bootdev_ai_agent
uv sync
cp .env.example .env
```

`.env.example` contains:

```env
OPENROUTER_API_KEY=your_key_here
```

---

## 🚀 Usage

```bash
uv run main.py "your prompt here"
uv run main.py --verbose "your prompt here"
```

Whether tools run depends on the model response. Tool path arguments are relative to the working directory `./calculator` (so `main.py` is `./calculator/main.py` when the process cwd is the repo root).

---

## 🧠 How it works

1. Builds `messages` with the system string from `prompts.py` and your user prompt  
2. `send_request` calls `client.chat.completions.create(..., tools=available_functions)`  
3. Appends the assistant message; for each `tool_call`, runs `call_function1` and appends the returned tool message  
4. Exits on a message with no `tool_calls`; after 20 iterations, if the last message still has `tool_calls`, prints `Error: Max iterations reached` and `exit(1)`

| Tool | Behavior in this repo |
|------|------------------------|
| `get_files_info` | `os.listdir` on a directory (default `"."`); each entry shows `file_size=... bytes` and `is_dir=...` |
| `get_file_content` | Reads a file as text; stops at 10000 characters and appends a truncation note if longer |
| `write_file` | Writes/overwrites text (`"w"`); calls `os.makedirs(..., exist_ok=True)` on the parent path |
| `run_python_file` | Requires a `.py` path; runs `["python", <file>, ...args]` with `cwd` = working dir, `timeout=30`; returns stdout/stderr (and exit code if non-zero) |

---

## 📁 Project layout

```text
bootdev_ai_agent/
├── main.py                 # CLI + API loop
├── prompts.py              # system_prompt string
├── call_function.py        # available_functions + call_function1
├── functions/              # get_files_info, get_file_content, write_file, run_python_file (+ schemas)
├── calculator/             # working directory passed into tools
├── test_*.py               # root tests: test_get_files_info, test_get_file_content, test_write_file, test_run_python_file
├── .env.example
├── pyproject.toml
└── uv.lock
```

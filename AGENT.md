AGENT.md
🤖 Project Persona & Mission

You are an autonomous Python developer agent. Your mission is to build a streamlined pipeline that extracts text from a specific PDF, generates a concise summary using the Gemini API, and dispatches that summary to a user via a Telegram Bot.
🛠 Tech Stack

    Language: Python 3.12+

    Package Manager: uv (Fast, disk-efficient Python package management)

    Version Control: Git

    Primary Libraries: * google-generativeai (for summarization)

        python-telegram-bot or requests (for Telegram integration)

        pypdf or pdfminer.six (for text extraction)

📋 Rules & Constraints

    Scoping: All operations, file creations, and executions must occur strictly inside the working directory.

    Command Whitelist: You are permitted to use only the following external commands:

        git (for staging and committing changes)

        cat (for reading files)

        head (for checking file previews)

        uv (for environment and dependency management)

    Git Protocol: Every logical change (e.g., adding a function, updating dependencies) must be staged and committed immediately with a clear, descriptive message.

    Simplicity: Avoid over-engineering. Prioritize readability and a "minimal viable product" approach. Do not add features not requested.

🏗 Project Workflow
1. Initialization

    The virtual enviroment is already initializated clean for you.
  
    Create a .env file for TELEGRAM_BOT_TOKEN, CHAT_ID, and MODEL_API_KEY.

2. PDF Extraction Module

    Implement a script that targets a specific file path.

    Extract the raw text content while handling basic encoding issues.

3. Summarization Logic

    Pass the extracted text to the model.

    Construct the code so that the model can be easily interchangeable

    Use a system prompt that ensures the "resume" is concise and formatted for mobile reading (Telegram).

4. Telegram Integration

    Use a simple POST request or a lightweight library to send the summary to the specified CHAT_ID.

5. Main Execution (main.py)

    A single entry point that orchestrates the flow: Load PDF → Extract → Summarize → Send.

6. Testing

    You should include a couple of tests to check correctness of: model resume, telegram bot and typing.

📂 Expected Directory Structure
Plaintext

.
├── .git/
├── .python-version
├── pyproject.toml
├── .env                # Ignored by git
├── README.md
├── AGENT.md            # This file
├── src/
    └── main.py         # Primary logic
└── tests
    └── main.py

📝 Commit Standard

    feat: initial project structure with uv

    feat: add pdf extraction logic

    feat: integrate gemini summarization

    feat: add telegram notification support

    fix: handle large pdf text chunks

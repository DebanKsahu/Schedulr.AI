# Schedulr.AI

Schedulr.AI is an intelligent scheduling assistant that leverages FastAPI, Google APIs, and modern LLM tools to help users schedule meetings, manage participants, and integrate seamlessly with Google Calendar using natural language.

## Features

- **Google OAuth2 Authentication**: Secure login with Google accounts.
- **Natural Language Scheduling**: Request meetings using plain English.
- **Google Calendar Integration**: Automatically creates and manages events.
- **LLM-powered Intent Recognition**: Advanced language models extract scheduling details and understand user intent.
- **Async & Scalable**: Built with FastAPI and async SQLAlchemy for high performance.
- **Extensible Agent Architecture**: Modular agent design for easy extension and maintenance.

## Tech Stack

- Python 3.12+
- FastAPI
- SQLAlchemy & SQLModel (async)
- Google API Python Client
- Authlib (OAuth2)
- LangChain, LangGraph, Google Gemini
- Uvicorn (ASGI server)
- PostgreSQL (recommended for production)

## Getting Started

### Prerequisites

- Python 3.12 or higher
- PostgreSQL database
- Google Cloud project with OAuth2 credentials

### Installation

1. **Clone the repository:**
	 ```sh
	 git clone https://github.com/DebanKsahu/Schedulr.AI.git
	 cd Schedulr.AI
	 ```

2. **Install dependencies using [uv](https://github.com/astral-sh/uv):**
	 ```sh
	 uv sync
	 ```

3. **Configure environment variables:**
	 - Set your Google OAuth2 credentials in `app/core/config.py` or as environment variables.
	 - Set up your PostgreSQL connection string.

4. **Start the server:**
	 ```sh
	 uv run uvicorn app.main:app --reload
	 ```

## API Overview

### Authentication

- `GET /auth/google/v1/login`  
	Initiates Google OAuth2 login flow.

- `GET /auth/google/v1/callback`  
	Handles OAuth2 callback and stores credentials.

### Scheduling

- `POST /schedule/v1/schedule_agent`  
	Accepts a scheduling request and returns the agent's response.

	**Request Body Example:**
	```json
	{
		"user_id": "string",
		"thread_id": "string",
		"user_query": "Schedule a meeting with Alice and Bob tomorrow at 3pm"
	}
	```

## Project Structure

```
app/
	main.py                # FastAPI app entrypoint
	agent/                 # Scheduling agent logic and tools
	api/v1/                # API routes (login, scheduling)
	core/                  # Config, utilities, enums
	database/              # Models and DB setup
	services/              # Google API integration
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements and bug fixes.

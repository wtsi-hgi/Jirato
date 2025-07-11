import os
from typing import Optional

import ollama
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pydantic import BaseModel

from jirato.helper import add_jira

load_dotenv()

app = FastAPI(
    title="Jirato Web App",
    description="Web interface for JIRA ticket creation with Ollama integration",
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration
OLLAMA_REMOTE_HOST = os.getenv(
    "OLLAMA_REMOTE_HOST", "http://ollama.hgi.sanger.ac.uk:11434"
)
DEFAULT_MODEL = "gemma3:27b"


# Pydantic models for structured outputs
class JiraTicketContent(BaseModel):
    summary: str
    description: str


class PreviewRequest(BaseModel):
    username: str
    project: str = "HI"
    prompt: str
    softpackAdmin: bool = False
    userStory: bool = False


class PreviewResponse(BaseModel):
    success: bool
    generated_content: Optional[JiraTicketContent] = None
    error: str = None


class TicketRequest(BaseModel):
    username: str
    project: str = "HI"
    summary: str
    description: str
    softpackAdmin: bool = False
    userStory: bool = False


class TicketResponse(BaseModel):
    success: bool
    jira_key: str = None
    jira_url: str = None
    error: str = None


async def check_model_exists(client: ollama.Client, model_name: str) -> bool:
    """Check if a model exists on the Ollama server"""
    try:
        models = client.list()
        # Fix: use .model attribute instead of ['name']
        available_models = [model.model for model in models["models"]]

        # Check exact match first
        if model_name in available_models:
            return True

        # Check if model name without tag matches any available model
        model_base = model_name.split(":")[0]
        for available in available_models:
            if available.startswith(model_base):
                logger.info(
                    f"Model {model_name} not found, but {available} is available"
                )
                return True

        logger.error(
            f"Model {model_name} not found. Available models: {available_models}"
        )
        return False

    except Exception as e:
        logger.error(f"Error checking model availability: {e}")
        return False


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    return FileResponse("static/index.html")


@app.post("/preview-ticket", response_model=PreviewResponse)
async def preview_ticket(request: PreviewRequest):
    """Generate ticket content preview using Ollama without creating the ticket"""
    try:
        logger.info(
            f"Generating preview for user: {request.username}, project: {request.project}"
        )

        # Configure Ollama client to use remote host
        client = ollama.Client(host=OLLAMA_REMOTE_HOST)

        # Check if model exists
        if not await check_model_exists(client, DEFAULT_MODEL):
            return PreviewResponse(
                success=False,
                error=f"Model {DEFAULT_MODEL} is not available on the Ollama server. Please ensure the model is installed.",
            )

        # Create a prompt for Ollama to generate structured response
        if request.userStory:
            ollama_prompt = f"""
Based on the following user request, generate a JIRA user story ticket using the Connextra template format.

The summary should follow the format: "As a [user], I want [feature] so that [benefit]"
The description should be detailed and well-formatted, including:
- Acceptance criteria
- Technical details
- Requirements
- Context

User request: {request.prompt}

Please structure the response as a proper user story with clear acceptance criteria.
"""
        else:
            ollama_prompt = f"""
Based on the following user request, generate a JIRA ticket with an appropriate summary and detailed description.

The summary should be concise (under 100 characters) and capture the main request.
The description should be detailed and well-formatted, including any technical details, requirements, or context.

User request: {request.prompt}
"""

        # Call Ollama with structured output using Pydantic schema
        logger.info(
            f"Calling Ollama with model {DEFAULT_MODEL} for structured content generation..."
        )
        response = client.chat(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": ollama_prompt,
                }
            ],
            format=JiraTicketContent.model_json_schema(),
            options={
                "temperature": 0
            },  # Set temperature to 0 for more deterministic output
        )

        ollama_content = response["message"]["content"].strip()
        logger.info(f"Ollama response: {ollama_content}")

        # Parse and validate the structured response using Pydantic
        try:
            ticket_data = JiraTicketContent.model_validate_json(ollama_content)
            logger.info(
                f"Generated preview: summary='{ticket_data.summary}', description length={len(ticket_data.description)}"
            )
        except Exception as e:
            logger.error(f"Failed to parse Ollama structured response: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to parse Ollama response: {str(e)}"
            )

        return PreviewResponse(success=True, generated_content=ticket_data)

    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}")
        return PreviewResponse(success=False, error=str(e))


@app.post("/create-ticket", response_model=TicketResponse)
async def create_ticket(request: TicketRequest):
    """Create a JIRA ticket with provided summary and description"""
    try:
        logger.info(
            f"Creating ticket for user: {request.username}, project: {request.project}, softpack_admin: {request.softpackAdmin}, user_story: {request.userStory}"
        )

        # Create JIRA ticket using existing function
        logger.info("Creating JIRA ticket...")
        jira_key = add_jira(
            summary=request.summary,
            description=request.description,
            done=False,
            labels=[],
            name=request.username,
            project_key=request.project,
            reporter=request.username,
            is_softpack_admin=request.softpackAdmin,
            is_user_story=request.userStory,
        )

        jira_url = f"https://jira.sanger.ac.uk/browse/{jira_key}"
        logger.info(f"Created JIRA ticket: {jira_url}")

        return TicketResponse(success=True, jira_key=jira_key, jira_url=jira_url)

    except Exception as e:
        logger.error(f"Error creating ticket: {str(e)}")
        return TicketResponse(success=False, error=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        client = ollama.Client(host=OLLAMA_REMOTE_HOST)
        model_available = await check_model_exists(client, DEFAULT_MODEL)

        return {
            "status": "healthy",
            "ollama_host": OLLAMA_REMOTE_HOST,
            "default_model": DEFAULT_MODEL,
            "model_available": model_available,
        }
    except Exception as e:
        return {
            "status": "error",
            "ollama_host": OLLAMA_REMOTE_HOST,
            "default_model": DEFAULT_MODEL,
            "model_available": False,
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

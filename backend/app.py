"""
Hugging Face Spaces entry point for the Todo API.

This file serves as the entry point for Hugging Face Spaces deployment.
It creates the FastAPI app instance that will be loaded by the Spaces runtime.
"""

from src.main import app

# This is the app instance that Hugging Face Spaces will load
# The Spaces runtime will look for an 'app' object in this file
# or in the main module specified in the Space configuration.

# The app is already configured with:
# - CORS middleware for cross-origin requests
# - Authentication routes under /auth
# - Todo routes under /todos  
# - Chat routes under /chat
# - Health check endpoints

# When deployed to Hugging Face Spaces, the app will be served at:
# https://<username>-<space-name>.hf.space

if __name__ == "__main__":
    # This allows running the app locally with uvicorn for testing
    import uvicorn
    uvicorn.run(
        "app:app",  # Points to this file's app object
        host="0.0.0.0",
        port=7860,  # Hugging Face Spaces default port
        reload=True
    )
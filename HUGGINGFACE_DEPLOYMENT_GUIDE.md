# Deploying the Todo App Backend to Hugging Face Spaces

This guide will walk you through deploying your FastAPI backend to Hugging Face Spaces using Docker.

## Prerequisites

1. A Hugging Face account (sign up at [huggingface.co](https://huggingface.co))
2. A Neon PostgreSQL database (free tier available)
3. Basic familiarity with Docker and Git

## Step 1: Prepare Your Database

1. Sign up for a free Neon account at [neon.tech](https://neon.tech)
2. Create a new project
3. Note down your connection string in the format:
   ```
   postgresql://username:password@ep-xyz.region.neon.tech/dbname?sslmode=require
   ```

## Step 2: Fork or Create the Repository

You have two options:

### Option A: Use the Existing Repository
1. Fork the repository: `https://github.com/maryamarif24/todo-app-phase-III.git`
2. Navigate to the `backend` directory

### Option B: Create a New Repository for the Backend
1. Create a new repository on GitHub
2. Copy only the `backend` directory contents to the new repository
3. Make sure to include:
   - `Dockerfile`
   - `requirements.txt`
   - `src/` directory with all source code
   - `.env.example`
   - `README.md` (the one with Hugging Face metadata)

## Step 3: Configure Hugging Face Space

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in the details:
   - **Space SDK**: Choose "Docker"
   - **Repository**: Either use your forked repository or the new repository with just the backend
   - **Hardware**: CPU (sufficient for development/testing)
   - **Visibility**: Public or Private (as per your preference)

## Step 4: Set Environment Variables

After creating the Space, go to the "Files" tab and click on "Environment Variables" (or "Settings" → "Secrets" depending on the UI):

Add these environment variables:

```
DATABASE_URL=postgresql://username:password@ep-xyz.region.neon.tech/dbname?sslmode=require
BETTER_AUTH_SECRET=generate-a-random-string-at-least-32-characters-long
FRONTEND_URL=https://your-frontend-app.vercel.app (or whatever your frontend URL will be)
```

To generate a secure `BETTER_AUTH_SECRET`, you can use:
```bash
openssl rand -base64 32
```

## Step 5: Understanding the Dockerfile

Your Dockerfile is already configured for Hugging Face Spaces:

```dockerfile
# Hugging Face Spaces Dockerfile for FastAPI Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

## Step 6: The Application Structure

Your application is organized as follows:
- `src/main.py` - Main FastAPI application
- `src/models/` - Database models and connection management
- `src/api/` - API route definitions
- `src/services/` - Business logic

## Step 7: API Endpoints

Once deployed, your API will be accessible at:
- `https://YOUR_USERNAME-space-name.hf.space/` - Health check
- `https://YOUR_USERNAME-space-name.hf.space/health` - Health status
- `https://YOUR_USERNAME-space-name.hf.space/docs` - Interactive API documentation
- `https://YOUR_USERNAME-space-name.hf.space/redoc` - Alternative API documentation

### Authentication Endpoints:
- `POST /auth/signup` - Register new user
- `POST /auth/signin` - Sign in user
- `POST /auth/signout` - Sign out user

### Todo Endpoints:
- `GET /todos` - List all todos
- `POST /todos` - Create new todo
- `GET /todos/{id}` - Get todo by ID
- `PUT /todos/{id}` - Update todo
- `PATCH /todos/{id}/toggle` - Toggle completion
- `DELETE /todos/{id}` - Delete todo

### Chat Endpoints:
- `POST /chat/completion` - Chat completion endpoint

## Step 8: Troubleshooting

### Common Issues:

1. **Database Connection Errors**: Ensure your `DATABASE_URL` is correctly formatted and accessible.
2. **Port Binding**: The application is configured to run on port 7860, which is required for Hugging Face Spaces.
3. **Environment Variables**: Double-check that all required environment variables are set in the Space settings.

### Checking Logs:
- Go to your Space page
- Click on the "Logs" tab to see real-time application logs
- Look for any error messages during startup

## Step 9: Connecting Frontend

To connect a frontend application to your deployed backend:

1. Update your frontend's API calls to point to your Space URL
2. For example, if your Space is at `https://myuser-todo-backend.hf.space`, update your API calls to use this base URL
3. Make sure your `FRONTEND_URL` environment variable includes your frontend domain for CORS

## Additional Notes

- The Space will automatically rebuild when you push changes to your connected repository
- Free Spaces go to sleep after 48 hours of inactivity
- For production use, consider upgrading to a paid Space for better performance and uptime

## Security Considerations

- Never commit secrets to your repository
- Use Hugging Face Space Secrets for sensitive information
- Rotate your `BETTER_AUTH_SECRET` periodically
- Monitor your database usage and set appropriate limits

## Scaling Considerations

- For increased traffic, consider upgrading your Space hardware
- Monitor your database connection pool settings
- Consider implementing caching for frequently accessed data
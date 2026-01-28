---
title: Worksy Todo API
emoji: ✅
colorFrom: pink
colorTo: red
sdk: docker
pinned: false
license: mit
---

# Worksy Todo API

A FastAPI backend for the Worksy Todo application.

## Features

- User authentication (signup, signin, signout)
- Todo CRUD operations
- PostgreSQL database (Neon)
- RESTful API design

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/signin` - Sign in user
- `POST /auth/signout` - Sign out user

### Todos
- `GET /todos` - List all todos
- `POST /todos` - Create new todo
- `GET /todos/{id}` - Get todo by ID
- `PUT /todos/{id}` - Update todo
- `PATCH /todos/{id}/toggle` - Toggle completion
- `DELETE /todos/{id}` - Delete todo

### Chat
- `POST /chat/completion` - Chat completion endpoint

### Health
- `GET /` - Health check
- `GET /health` - Health status

## Deployment to Hugging Face Spaces

This application is configured for deployment to Hugging Face Spaces using Docker.

### Quick Deployment Steps:

1. Create a Space with Docker SDK
2. Set the following environment variables in Space settings:
   - `DATABASE_URL` - Neon PostgreSQL connection string
   - `BETTER_AUTH_SECRET` - Secret for auth tokens (at least 32 chars)
   - `FRONTEND_URL` - Frontend URL for CORS (optional, defaults to common dev URLs)

3. The application will be available at `https://<your-username>-<space-name>.hf.space`

### Environment Variables

Set these in your Hugging Face Space settings:

- `DATABASE_URL` - Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET` - Secret for auth tokens (generate with: `openssl rand -base64 32`)
- `FRONTEND_URL` - Frontend URL for CORS (comma-separated if multiple)

## Local Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Run the application
uvicorn src.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000` with docs at `http://localhost:8000/docs`

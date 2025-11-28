# Mental Health Assistant Chatbot

A mental health support chatbot that provides guidance and information about mental health and well-being using Google's Gemini AI with RAG (Retrieval-Augmented Generation) capabilities.

## Project Overview

Mental Health Assistant is an AI-powered chatbot designed to provide supportive mental health guidance. It uses:
- Gemini API for natural language processing
- RAG (Retrieval-Augmented Generation) for context-aware responses
- A knowledge base focused on mental health and wellness
- Supportive, evidence-informed responses for better user experience

## Tech Stack

### Backend
- Python 3.11
- Django REST Framework
- Google Gemini API
- RAG implementation with document embeddings

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- Framer Motion for animations

## Project Structure

```
mental-health-chatbot/
├── Backend_new/
│   ├── chat_api/
│   │   ├── services/
│   │   │   ├── chat_service.py    # Gemini API integration
│   │   │   └── document_store.py  # RAG implementation
│   │   ├── views.py              # API endpoints
│   │   └── urls.py
│   ├── knowledge_base/           # RAG document storage
│   └── digibuddy/               # Django settings (project name)
├── src/
│   ├── components/
│   │   ├── Chatbot.tsx         # Main chat interface
│   │   ├── ChatInput.tsx       # Message input
│   │   └── ui/                 # Reusable components
│   ├── services/
│   │   └── chatService.ts      # API communication
│   └── App.tsx
└── public/
```

## Features

- **Streaming Responses**: Real-time, character-by-character response generation
- **RAG Integration**: Context-aware responses using document knowledge base
- **Source Attribution**: Transparent source citations for information
- **Adaptive UI**: Responsive design with loading states
- **Error Handling**: Graceful error management with user feedback

## Setup and Installation

### Prerequisites
- Python 3.11+
- Node.js 16+
- Google Gemini API key

### Backend Setup

1. Create a virtual environment:
```bash
cd Backend_new
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create your environment file by copying the template:
```bash
cd Backend_new
cp env.example .env  # Windows: copy env.example .env
```
Then edit `.env` and add your Gemini key:
```
GEMINI_API_KEY=your_api_key_here
```

4. Add Google OAuth credentials (required for login):
```
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback/
FRONTEND_APP_URL=http://localhost:5173
```
Create the OAuth Client ID in Google Cloud Console (Web application) and add `http://localhost:8000/api/auth/google/callback/` as an authorized redirect URI.

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Create your frontend environment file:
```bash
cp env.example .env  # Windows: copy env.example .env
```
Update `VITE_API_BASE_URL` if your backend does not run on `http://localhost:8000/api`.

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

### Google OAuth Flow

1. From the frontend, visit `/login` and click **Continue with Google**.
2. The backend endpoint `/api/auth/google/login/` generates a secure Google OAuth URL and returns it to the browser.
3. After consenting at Google, the backend callback exchanges the code for Google tokens, creates/updates the user, and issues JWT access/refresh tokens via SimpleJWT.
4. The backend redirects back to the frontend `/auth/callback` route, which stores the tokens and loads the user profile.
5. Authenticated routes (like `/chat`) require a valid bearer token; the chatbot now includes a Logout button to clear tokens.

If you change ports or deploy, update `FRONTEND_APP_URL`, `GOOGLE_REDIRECT_URI`, and `VITE_API_BASE_URL` accordingly.

## RAG Implementation

The project uses Retrieval-Augmented Generation to enhance responses:

1. **Document Storage**: Knowledge base documents are stored in `Backend_new/knowledge_base/`
2. **Embedding Generation**: Documents are embedded using Gemini's embedding model
3. **Similarity Search**: User queries are matched against document embeddings
4. **Context Integration**: Relevant document sections are included in prompts

### Adding Documents to RAG

Use the provided script:
```bash
cd Backend_new
python add_document.py "path/to/document.txt" "Document Name"
```

## API Endpoints

### POST /api/chat/
Handles chat interactions with streaming responses.

Request:
```json
{
  "message": "string",
  "chat_history": []
}
```

Response (Server-Sent Events):
```json
{
  "response": "string",
  "status": "streaming|success|error",
  "done": boolean
}
```

## Error Handling

The system includes comprehensive error handling:
- API key validation
- Streaming connection management
- Rate limiting
- Timeout handling
- User feedback for errors

## License

MIT License - See LICENSE file for details

# EcoSort AI backend

Node.js + Express + MongoDB + Groq/OpenAI-compatible vision and chat backend for the existing frontend.

## Setup

```powershell
cd backend
Copy-Item .env.example .env
npm install
npm start
```

Set `MONGODB_URI` and `AI_API_KEY` in `backend/.env`. When you run from `backend/`, the existing project-root `.env` is also read as a fallback for `MONGODB_URI`. The backend does not classify from filenames or return a fixed waste type. `POST /api/scans/analyze` requires a real image upload and sends its bytes to the configured vision model.

## API

- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/user/:id`
- `PUT /api/auth/user/:id`
- `POST /api/scans/analyze` multipart form fields: `image`, `userId`
- `POST /api/scans/:id/sort` JSON: `{ "selectedBin": "RECYCLABLE" }`
- `GET /api/scans/:id`
- `GET /api/rewards?userType=STUDENT`
- `POST /api/rewards/:rewardId/redeem`
- `GET /api/missions?userType=RESIDENT`
- `GET /api/leaderboards?userType=STUDENT`
- `POST /api/reports`
- `POST /api/chat/start` creates a session, greets the user, and asks for credentials.
- `POST /api/chat/message` accepts the first credential message, creates the profile, then answers relevant EcoBot questions.

The scan flow is two-step: analyze the actual image first, then submit the user's selected bin. XP, credits, and leaderboard score are updated only after the bin is evaluated as correct.

Chat and vision calls use `temperature: 1.5`. API keys remain server-side. The first chatbot message must provide a username, `STUDENT` or `RESIDENT`, and a registration number or employee/resident ID. No normal chatbot answer is generated until that profile is created.

# Technical Architecture

```text
React + Vite dashboard
        |
        | HTTP / JSON + multipart image upload
        v
FastAPI application
  |-- Food recognition + nutrition
  |-- Freshness visual screening
  |-- Kitchen hygiene visual review
  |-- Cooking assistant
  |-- Personalized meal planner
        |
        | Gemini API (optional, server-side key)
        v
Google Generative Language API

Local JSON activity history (starter persistence)
```

## Request flow
1. The React client collects text preferences or an image.
2. FastAPI validates request shape and image type/size.
3. If `GEMINI_API_KEY` is configured, the backend calls the configured Gemini model.
4. If no key is configured, a clearly labeled illustrative fallback is returned.
5. The result is rendered in the dashboard and recorded in local activity history.

## Production hardening
- Replace local JSON history with MongoDB or PostgreSQL and authenticated user-scoped records.
- Add rate limiting, authentication, audit logging and upload retention/deletion controls.
- Store secrets in deployment environment variables.
- Add structured monitoring and model output validation.
- Validate AI-generated nutrition against a trusted food composition database.
- Treat food-safety and hygiene output as decision support only, never certification.

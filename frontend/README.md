# AI Business Idea Validator - Frontend

React-based frontend for the AI Business Idea Validator application.

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── IdeaForm.js
│   │   └── AnalysisResults.js
│   ├── pages/
│   ├── services/
│   │   └── api.js
│   ├── styles/
│   │   ├── App.css
│   │   ├── IdeaForm.css
│   │   └── AnalysisResults.css
│   ├── App.js
│   └── index.js
└── package.json
```

## Installation & Setup

### Prerequisites
- Node.js 14+ and npm

### Steps

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# The app will open at http://localhost:3000
```

### Build for Production

```bash
npm run build
```

## Features

✅ Business idea submission form
✅ AI-powered analysis results
✅ Score visualization
✅ Responsive design
✅ API integration with FastAPI backend

## Environment Variables

Create `.env` file:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## Available Scripts

- `npm start` - Run development server
- `npm build` - Build for production
- `npm test` - Run tests

## API Integration

The frontend connects to the backend at `http://localhost:8000/api/v1`

### Key Endpoints Used

- `POST /ideas/` - Submit new idea
- `GET /analysis/{idea_id}` - Get analysis results
- `POST /analysis/{idea_id}/analyze` - Trigger analysis

## Components

### IdeaForm
Form for submitting business ideas with all required fields

### AnalysisResults
Displays analysis results with scores and insights

## Styling

Modern gradient design with responsive layout
- Color scheme: Purple gradient (#667eea - #764ba2)
- Mobile-friendly responsive design
- Smooth transitions and hover effects

---

**Status**: Ready for Production
**Version**: 1.0.0
**Date**: April 14, 2026

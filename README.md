# EPL_ML_project
## Overview
This project aims to predict English Premier League (EPL) match outcomes using machine learning techniques. The model is trained on historical match data and various features such as team statistics, player performance, and more.

## Features
- Data preprocessing and feature engineering
- Multiple machine learning models for prediction
- Model evaluation and comparison
- Visualization of results


## Design

### 🧩 System Design

#### 📌 Overview

The EPL Predictor Web App is a full-stack application that predicts the outcome of English Premier League (EPL) matches using machine learning. It is transitioning from a Streamlit-based UI to a decoupled architecture with a React frontend and FastAPI backend for improved scalability and user experience.

#### ⚙️ Architecture
```
[React Frontend] <---> [FastAPI Backend API] <---> [ML Model & Utilities]
                                    |
                                    V
                          [Database / Data Storage]
```
- Frontend: Built in React with TypeScript and TailwindCSS
- Backend: Built in FastAPI with Python
- Model Pipeline: Includes data scraping, cleaning, training, and prediction modules
- Data Storage: Models and datasets stored locally or in cloud (S3/DB planned)

📁 Directory Structure
```bash
EPL_ML_PREDICTOR/
│
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entrypoint
│   │   ├── api/endpoints/        # Routes: predict, train, etc.
│   │   ├── core/                 # Configs and utils
│   │   ├── models/               # Pydantic request/response models
│   │   ├── services/             # ML logic: predict, train, scrape
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/           # React UI components
│   │   ├── pages/                # Route pages (predict, train, about)
│   │   ├── services/             # API handlers using Axios
│   │   └── App.tsx
│   └── package.json
│
└── README.md
```

#### 🚀 Core Features

#### MVP
- 🧠 Predict match result between two EPL teams
- 📊 View predicted probabilities (Win/Draw/Loss)
- 🔁 Trigger model retraining via admin control
- 🏷️ Dynamic dropdown for EPL teams

#### Backend Endpoints (FastAPI)
| Method | Route       | Description                      |
|--------|-------------|----------------------------------|
| POST   | `/predict`  | Returns prediction from model    |
| POST   | `/train`    | Triggers full training pipeline  |
| GET    | `/fixtures` | Returns all or filtered fixtures |
| GET    | `/teams`    | Returns list of EPL teams        |
| GET    | `/status`   | Healthcheck                      |


#### Frontend UI

#### Stack
- React + TypeScript
- Tailwind CSS
- Axios for API communication
- React Router for navigation
- Recharts for data visualization (optional)

#### Key Components
- PredictionForm: Select home and away teams
- PredictionResult: Show results with probabilities
- TeamSelector: Dynamic team dropdowns
- TrainModelButton: Admin action to retrain model


#### 🐳 Deployment
- Dockerized frontend and backend
- Optional: Nginx as reverse proxy
- Supports deployment to:
- Render / Railway / Fly.io
- AWS EC2 or Lightsail
- Docker Compose (local)


#### 🧪 Testing

Backend (FastAPI)
- pytest for unit and integration tests
- FastAPI test client with mock routes

Frontend (React)
- React Testing Library + Jest
- API mocking with MSW (Mock Service Worker)


#### Future Enhancements
- User authentication & favorites
- Live match integration (e.g., with football-data.org API)
- Cloud model storage (AWS S3)
- Model versioning & evaluation dashboard

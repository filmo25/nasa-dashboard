# NASA TechPort Dashboard

## Quick Start Guide

Follow these steps to set up and run the application using Docker Compose:

! Note: compose build requires buildx 0.17.0 or later

### 1. Configure Environment Variables
Create a `.env` file inside the `app/` directory (or copy `.env.example`):
```bash
cp app/.env.example app/.env
```
Add your NASA API key to `app/.env`:
```env
NASA_API_KEY=your_nasa_api_key_here
```

### 2. Launch the Application
Start the containerized stack from the project root:
```bash
docker-compose up --build
```

### 3. Access the App
Open your browser and navigate to:
```
http://localhost:5000
```
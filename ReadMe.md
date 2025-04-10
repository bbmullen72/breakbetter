# BreakBetter

An AI-powered study and break recommendation system that helps optimize your study sessions and breaks based on various factors.

## Key Features

- Smart study interval recommendations based on:
  - Mental energy level (high/low intensity tasks)
  - Time of day (morning/evening)
  - Deadline pressure
- Personalized break activities considering:
  - Screen usage
  - Activity level
  - Energy level
  - Personal preferences
- Study tips and focus recommendations

## How to Run This App

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- MongoDB account (you can get a free one at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas))
- OpenAI API key (you can get one at [OpenAI](https://platform.openai.com/))

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/breakbetter.git
cd breakbetter
```

### Step 2: Set Up Environment Variables
1. Create a `.env` file in the backend directory:
```bash
cd backend
touch .env
```

2. Add your environment variables to `.env`:
```
MONGODB_URL=your_mongodb_connection_string
OPENAI_API_KEY=your_openai_api_key
```

```bash
echo ".env" >> .gitignore
```

### Step 3: Set Up Backend
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload
```

### Step 4: Set Up Frontend
```bash
# Open a new terminal window
cd frontend

# Install dependencies
npm install

# Start the frontend development server
npm start
```

### Step 5: Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
breakbetter/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── .env             # Environment variables (not in git)
└── frontend/
    ├── src/
    │   ├── components/  # Reusable UI components
    │   ├── pages/       # Application pages
    │   └── App.js       # Main application component
    └── public/          # Static assets
```


## Tech Stack

- **Backend**: FastAPI, MongoDB, OpenAI
- **Frontend**: React, TailwindCSS



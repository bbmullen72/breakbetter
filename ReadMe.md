# BreakBetter

An AI-powered application that provides personalized study and break recommendations based on various factors including mental energy, time of day, and personal preferences.

## Features

- Smart study interval recommendations
- Personalized break activities
- Consideration of screen usage and activity level
- Energy level-based suggestions
- Study tips and focus recommendations

## Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Environment Variables

Create a `.env` file in the backend directory:
```
MONGODB_URL=your_mongodb_connection_string
OPENAI_API_KEY=your_openai_api_key
```

## Tech Stack

- Backend: FastAPI, MongoDB, OpenAI
- Frontend: React, TailwindCSS

## API Endpoints
- POST /api/profile - Create/update user profile
- POST /api/recommend - Get break recommendations

## License
MIT License

## Project Structure

```
breakbetter/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.js
│   ├── package.json
│   └── public/
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- OpenAI for providing the GPT-3.5 API
- FastAPI team for the amazing web framework
- React and TailwindCSS communities for their excellent tools

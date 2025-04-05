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

## Quick Start

1. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

2. **Frontend Setup**
```bash
cd frontend
npm install
npm start
```

3. **Environment Setup**
Create `.env` in backend directory:
```
MONGODB_URL=your_mongodb_connection_string
OPENAI_API_KEY=your_openai_api_key
```

## Project Structure

```
breakbetter/
├── backend/
│   ├── main.py           # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── .env             # Environment variables
└── frontend/
    ├── src/
    │   ├── components/  # Reusable UI components
    │   ├── pages/       # Application pages
    │   └── App.js       # Main application component
    └── public/          # Static assets
```

## API

- `POST /api/profile` - Create/update user profile
- `POST /api/recommend` - Get personalized recommendations

## Tech Stack

- **Backend**: FastAPI, MongoDB, OpenAI
- **Frontend**: React, TailwindCSS

## License
MIT License

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

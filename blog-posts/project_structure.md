project/
├── app/
│   ├── __init__.py
│   ├── database.py      # MongoDB and GridFS handling
│   ├── models.py        # Pydantic models
│   ├── services.py      # PDF processing and business logic
│   ├── main.py         # FastAPI endpoints
│   └── config.py       # Configuration settings
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_services.py
│   └── test_main.py
└── README.md
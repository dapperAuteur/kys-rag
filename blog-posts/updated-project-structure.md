science_decoder/
├── app/
│   ├── __init__.py
│   ├── models.py          # Pydantic models for data validation
│   ├── database.py        # MongoDB Atlas connection and operations
│   ├── services.py        # Business logic and AI processing
│   ├── main.py           # FastAPI endpoints
│   └── config.py         # Configuration settings
├── tests/
│   ├── __init__.py
│   ├── test_models.py    # Model validation tests
│   ├── test_database.py  # Database operation tests
│   ├── test_services.py  # Service logic tests
│   └── test_main.py      # API endpoint tests
├── .env                  # Environment variables (gitignored)
├── .env.template         # Template for environment variables
├── .gitignore           # Git ignore file
├── requirements.txt      # Python dependencies
├── pytest.ini           # Pytest configuration
└── README.md            # Project documentation

Key Directories and Files:
1. app/: Core application code
   - models.py: Data models with Pydantic validation
   - database.py: MongoDB operations with vector search
   - services.py: Business logic and AI processing
   - main.py: FastAPI routes and endpoints
   - config.py: Configuration management

2. tests/: Comprehensive test suite
   - Separate test files for each module
   - Includes integration tests
   - Uses pytest for testing

3. Configuration Files:
   
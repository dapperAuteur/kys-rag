# Science Article Checker: Complete Project Structure

Welcome to our project's file organization guide! Think of this like a map of a big building, where every room (folder) has a specific purpose and contains particular items (files). We'll walk through each section and explain what everything does in simple terms.

## The Main Building (Root Directory)

```
science-clickbait-rag/
│
├── README.md                    # The main welcome guide
├── CODE_OF_CONDUCT.md          # Rules for working together
├── CONTRIBUTING.md             # How to help improve the project
├── DISCUSSIONS.md              # Guide for community conversations
├── LICENSE                     # Legal permissions
└── package.json                # List of project needs
```

## Community and Support Area (.github folder)

```
.github/
├── FUNDING.yml                 # Ways to support the project
├── ISSUE_TEMPLATE/            
│   ├── bug_report.md          # Form for reporting problems
│   └── feature_request.md     # Form for suggesting new features
└── workflows/
    ├── tests.yml              # Automatic testing setup
    └── deploy.yml             # Automatic update setup
```

## Main Working Area (src folder)

### Website Section (Frontend)
```
src/frontend/
├── components/                 # Reusable webpage parts
│   ├── Layout/
│   │   ├── Header.tsx         # Top of page design
│   │   ├── Footer.tsx         # Bottom of page design
│   │   └── Navigation.tsx     # Menu system
│   ├── Chat/
│   │   ├── ChatWindow.tsx     # Where conversations happen
│   │   └── MessageBubble.tsx  # Individual message design
│   └── Forms/
│       ├── ArticleSubmit.tsx  # Article upload form
│       └── StudySubmit.tsx    # Study upload form
├── pages/
│   ├── index.tsx              # Home page
│   ├── chat.tsx               # Chat system page
│   ├── submit.tsx             # Upload page
│   └── about.tsx              # Information page
└── styles/
    ├── globals.css            # Main look and feel
    └── components.css         # Special design elements
```

### Server Section (Backend)
```
src/backend/
├── api/
│   ├── routes/
│   │   ├── articles.py        # Article handling
│   │   ├── studies.py         # Study handling
│   │   └── chat.py           # Chat system
│   └── middleware/
│       ├── auth.py           # Security checks
│       └── validation.py     # Input checking
├── database/
│   ├── models/
│   │   ├── article.py        # Article information structure
│   │   └── study.py         # Study information structure
│   └── connections/
│       ├── mongo.py         # Database connection
│       └── faiss.py        # Search system connection
└── services/
    ├── nlp/
    │   ├── embedding.py     # Text understanding system
    │   └── analysis.py     # Text checking system
    ├── vector_store/
    │   └── faiss_store.py  # Search organization
    └── rag/
        └── generator.py    # Answer creation system
```

### Shared Resources
```
src/shared/
├── types/
│   ├── article.ts           # Article data rules
│   └── study.ts            # Study data rules
└── utils/
    ├── formatting.ts       # Text cleaning tools
    └── validation.ts      # Data checking tools
```

## Testing Area
```
tests/
├── frontend/
│   ├── components/        # Testing webpage parts
│   └── pages/            # Testing full pages
└── backend/
    ├── api/              # Testing server responses
    ├── database/         # Testing data storage
    └── services/         # Testing helper systems
```

## Documentation Zone
```
docs/
├── api/
│   └── openapi.yaml     # API instruction manual
├── blog/
│   ├── part-1.md        # First tutorial
│   ├── part-2.md        # Second tutorial
│   └── images/          # Tutorial pictures
└── guides/
    ├── installation.md  # Setup instructions
    └── deployment.md    # Launch instructions
```

## Public Resources
```
public/
├── images/             # Website pictures
├── icons/             # Website symbols
└── assets/            # Other resources
```

## Understanding How It All Works Together

Imagine our project like a newsroom that fact-checks science articles:

1. **Front Desk (Frontend)**: This is where visitors interact with our system. Just like a newspaper's front desk, it handles:
   - Taking article submissions (like letters to the editor)
   - Answering questions (like reader services)
   - Showing results (like publishing articles)

2. **Research Department (Backend)**: Behind the scenes, this is where the real work happens:
   - Fact-checkers (API routes) receive and direct requests
   - Researchers (Services) analyze articles and studies
   - Filing system (Database) keeps everything organized
   - Search team (FAISS) finds relevant information quickly

3. **Quality Control (Tests)**: Just like newspaper editors, these files make sure everything is accurate and working properly.

4. **Employee Handbook (Docs)**: These files help new team members understand how everything works.

Each file and folder has a specific job, just like each person in a newsroom has a specific role. When they all work together, we can help people understand science articles better and spot misleading information.

## For Technical Leaders

This structure demonstrates several professional best practices:

1. **Clear Separation of Concerns**: Frontend, backend, and shared code are kept separate and organized.
2. **Type Safety**: TypeScript and Python type hints ensure code reliability.
3. **Testing Coverage**: Comprehensive test structure for all components.
4. **Documentation**: Thorough documentation for both users and developers.
5. **Scalability**: Modular design allows for easy expansion.

## For Business Decision Makers

This organization shows:
1. Professional-grade architecture
2. Easy maintenance and updates
3. Clear documentation for new team members
4. Strong community support structure
5. Security and reliability considerations

Would you like to learn more about any specific part of the structure?
# Frontend Dependencies & Setup

## Core Dependencies
```json
{
  "dependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.3.0",
    "@mui/material": "^5.11.0",
    "@emotion/react": "^11.10.0",
    "@emotion/styled": "^11.10.0",
    "@mui/icons-material": "^5.11.0",
    "@tanstack/react-query": "^4.24.0",
    "react-hook-form": "^7.43.0",
    "@hookform/resolvers": "^2.9.0",
    "yup": "^1.0.0",
    "recharts": "^2.5.0"
  },
  "devDependencies": {
    "@types/jest": "^29.4.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^5.16.0",
    "@testing-library/user-event": "^14.4.0",
    "eslint-config-prettier": "^8.6.0",
    "prettier": "^2.8.0"
  }
}
```

## Environment Variables
```env
REACT_APP_API_GATEWAY_URL=http://localhost:8000
REACT_APP_AUTH_SERVICE_URL=http://localhost:8001
REACT_APP_CONTENT_SERVICE_URL=http://localhost:8002
REACT_APP_ASSIGNMENT_SERVICE_URL=http://localhost:8004
REACT_APP_ENVIRONMENT=development
```

## Project Structure
```
frontend/
├── public/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── common/          # Common components (Button, Input, etc.)
│   │   ├── layout/          # Layout components (Header, Sidebar, etc.)
│   │   └── forms/           # Form components
│   ├── pages/               # Page components
│   │   ├── auth/           # Authentication pages
│   │   ├── courses/        # Course management pages
│   │   ├── assignments/    # Assignment pages
│   │   └── dashboard/      # Dashboard pages
│   ├── services/           # API service functions
│   │   ├── api.ts          # Base API configuration
│   │   ├── auth.service.ts # Authentication APIs
│   │   ├── content.service.ts # Content APIs
│   │   └── assignment.service.ts # Assignment APIs
│   ├── hooks/              # Custom React hooks
│   │   ├── useAuth.ts      # Authentication hook
│   │   ├── useApi.ts       # API hook
│   │   └── useLocalStorage.ts # Local storage hook
│   ├── context/            # React Context providers
│   │   ├── AuthContext.tsx # Auth state management
│   │   └── ApiContext.tsx  # API state management
│   ├── utils/              # Helper functions
│   │   ├── constants.ts    # App constants
│   │   ├── validation.ts   # Form validation schemas
│   │   └── helpers.ts      # Utility functions
│   ├── types/              # TypeScript type definitions
│   │   ├── auth.types.ts   # Auth related types
│   │   ├── content.types.ts # Content related types
│   │   └── assignment.types.ts # Assignment related types
│   ├── styles/             # Global styles
│   │   ├── globals.css     # Global CSS
│   │   └── theme.ts        # Material-UI theme
│   └── App.tsx             # Main App component
├── package.json
└── README.md
```

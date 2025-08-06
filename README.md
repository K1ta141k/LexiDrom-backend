# LexiDrom

A sophisticated text comparison and analysis service built with FastAPI, featuring Google OAuth authentication, Supabase integration, and advanced AI-powered text processing capabilities.

## 🚀 Features

- **Text Comparison**: Advanced text similarity analysis and comparison
- **Google OAuth**: Secure authentication with Google accounts
- **Supabase Integration**: Real-time database operations and user management
- **AI-Powered Analysis**: Integration with Google's Gemma-3n model for text processing
- **Activity Tracking**: Comprehensive user activity monitoring
- **RACE Dataset**: Educational text dataset integration for learning analytics
- **Audio Transcription**: Speech-to-text capabilities (planned feature)
- **Cloud Ready**: Optimized for Google Cloud Platform deployment

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **Authentication**: Google OAuth, JWT tokens
- **Database**: Supabase (PostgreSQL)
- **AI/ML**: Google Generative AI (Gemma-3n), HuggingFace Datasets
- **Deployment**: Google Cloud Run, Docker
- **Monitoring**: Cloud Logging, Health checks

## 📋 Prerequisites

- Python 3.12+
- Google Cloud Platform account
- Supabase project
- Google OAuth credentials
- Google Generative AI API key

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/lexidrom.git
cd lexidrom
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Run the application**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Environment Variables

Create a `.env` file with the following variables:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key

# Google Generative AI
GOOGLE_API_KEY=your_google_ai_key
```

## 🏗️ Project Structure

```
lexidrom/
├── app/
│   ├── api/                 # API route handlers
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── activities.py   # Activity tracking
│   │   ├── text_comparison.py  # Text comparison logic
│   │   └── random_text.py  # Random text generation
│   ├── core/               # Core application logic
│   │   └── auth.py         # Authentication utilities
│   ├── models/             # Data models and schemas
│   │   └── schemas.py      # Pydantic schemas
│   ├── services/           # Business logic services
│   │   ├── activity_tracker.py
│   │   ├── supabase_manager.py
│   │   ├── race_dataset_service.py
│   │   └── audio_transcription_service.py
│   └── utils/              # Utility functions
├── config/                 # Configuration files
├── tests/                  # Test files
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── cloudbuild.yaml        # CI/CD configuration
├── service.yaml           # Cloud Run service config
├── deploy.sh              # Deployment script
└── README.md              # This file
```

## 🔧 API Endpoints

### Authentication
- `POST /auth/google` - Google OAuth authentication
- `POST /auth/refresh` - Refresh JWT token
- `GET /auth/me` - Get current user info

### Text Comparison
- `POST /compare-texts/` - Compare text similarity (main endpoint)
- `POST /compare-texts/public` - Public text comparison endpoint
- `GET /compare-texts/history` - Get comparison history

### Activities
- `GET /activities/user/{user_id}` - Get user activities
- `POST /activities/log` - Log new activity
- `GET /activities/analytics` - Activity analytics

### Random Text
- `GET /random-text/race` - Get random RACE dataset text
- `GET /random-text/custom` - Get custom random text

### Health Checks
- `GET /` - Basic health check
- `GET /health` - Detailed health status

## 🔌 External APIs Used

### 1. Google Generative AI API
- **Purpose**: Advanced text comparison and analysis
- **Model**: Gemma-3n-e4b-it
- **Environment Variable**: `GOOGLE_API_KEY`
- **Features**: 
  - AI-powered text similarity analysis
  - Multiple reading mode support (skimming, comprehension, study, etc.)
  - Detailed feedback with accuracy scores
  - Fallback to simple comparison when API unavailable

### 2. Supabase API
- **Purpose**: Database operations and user management
- **Environment Variables**: `SUPABASE_URL`, `SUPABASE_KEY`
- **Features**:
  - User authentication and management
  - Activity tracking and analytics
  - Real-time database operations
  - PostgreSQL backend

### 3. Google OAuth API
- **Purpose**: User authentication
- **Environment Variables**: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- **Features**:
  - Secure Google account authentication
  - JWT token generation and verification
  - User session management

### 4. HuggingFace Datasets API
- **Purpose**: RACE dataset access for random text generation
- **Authentication**: Not required (public dataset)
- **Features**:
  - Educational text dataset integration
  - Random text generation for testing
  - 27,827 passages from English exams

## 🚀 Deployment

### Google Cloud Run Deployment

1. **Install Google Cloud SDK**
```bash
# Follow instructions at: https://cloud.google.com/sdk/docs/install
```

2. **Authenticate and set up project**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

3. **Deploy using the provided script**
```bash
./deploy.sh YOUR_PROJECT_ID us-central1
```

4. **Set environment variables**
```bash
gcloud run services update lexidrom \
    --region=us-central1 \
    --set-env-vars="SUPABASE_URL=your-url,SUPABASE_KEY=your-key,GOOGLE_CLIENT_ID=your-client-id,GOOGLE_CLIENT_SECRET=your-client-secret,JWT_SECRET_KEY=your-jwt-secret,GOOGLE_API_KEY=your-google-ai-key"
```

### Manual Deployment

```bash
# Build and push image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/lexidrom

# Deploy to Cloud Run
gcloud run deploy lexidrom \
    --image gcr.io/YOUR_PROJECT_ID/lexidrom \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --timeout 300 \
    --concurrency 80
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_audio_transcription.py
```

## 📊 Monitoring

### Health Checks
- Root endpoint: `GET /`
- Detailed health: `GET /health`

### Logs
```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=lexidrom" --limit=50
```

### Metrics
Monitor performance in the [Google Cloud Console](https://console.cloud.google.com/run/detail/us-central1/lexidrom/metrics)

## 🔒 Security

- **Authentication**: Google OAuth with JWT tokens
- **HTTPS**: Automatically provided by Cloud Run
- **CORS**: Configured for production domains
- **Environment Variables**: Secure storage of sensitive data
- **Input Validation**: Pydantic schemas for data validation

## 🛠️ Development

### Adding New Features

1. Create new API routes in `app/api/`
2. Add business logic in `app/services/`
3. Define schemas in `app/models/schemas.py`
4. Add tests in `tests/`
5. Update documentation

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to functions
- Write comprehensive tests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the inline code comments
- **Cloud Issues**: Refer to [Google Cloud documentation](https://cloud.google.com/run/docs)

## 🔄 Version History

- **v1.0.0**: Initial release with core text comparison features
- **v1.1.0**: Added audio transcription capabilities
- **v1.2.0**: Enhanced with RACE dataset integration
- **v1.3.0**: Cloud Run deployment optimization

---

**LexiDrom** - Advanced text analysis and comparison platform 
# LexiDrom Deployment Guide

This guide provides step-by-step instructions for deploying LexiDrom to Google Cloud Platform Cloud Run.

## Prerequisites

### 1. Google Cloud Account
- Create a Google Cloud account at [cloud.google.com](https://cloud.google.com)
- Enable billing for your project
- Install Google Cloud SDK

### 2. Required APIs
Enable the following APIs in your Google Cloud project:
- Cloud Build API (`cloudbuild.googleapis.com`)
- Cloud Run Admin API (`run.googleapis.com`)
- Container Registry API (`containerregistry.googleapis.com`)

### 3. Environment Variables
Prepare the following environment variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase service role key
- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `GOOGLE_API_KEY`: Your Google Generative AI API key

## Quick Deployment

### Option 1: Automated Deployment (Recommended)

1. **Clone and prepare the repository**
```bash
git clone https://github.com/yourusername/lexidrom.git
cd lexidrom
```

2. **Install Google Cloud SDK**
```bash
# Windows
# Option 1: Using winget (if the above doesn't work, try this)
winget install Google.CloudSDK --include-unknown

# Option 2: Manual installation
# Download from: https://cloud.google.com/sdk/docs/install#windows
# Run the installer and follow the prompts

# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

3. **Authenticate with Google Cloud**
```bash
gcloud auth login
gcloud auth application-default login
```

4. **Set your project**
```bash
gcloud config set project YOUR_PROJECT_ID
```

5. **Enable required APIs**
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

6. **Deploy using the script**
```bash
./deploy.sh YOUR_PROJECT_ID us-central1
```

7. **Set environment variables**
```bash
gcloud run services update lexidrom \
    --region=us-central1 \
    --set-env-vars="SUPABASE_URL=your-supabase-url,SUPABASE_KEY=your-supabase-key,GOOGLE_CLIENT_ID=your-google-client-id,GOOGLE_CLIENT_SECRET=your-google-client-secret,JWT_SECRET_KEY=your-jwt-secret,GOOGLE_API_KEY=your-google-ai-key"
```

### Option 2: Manual Deployment

1. **Build and push the Docker image**
```bash
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_NAME="lexidrom"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Build and push
gcloud builds submit --tag $IMAGE_NAME
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --timeout 300 \
    --concurrency 80 \
    --set-env-vars PORT=8080
```

3. **Set environment variables**
```bash
gcloud run services update lexidrom \
    --region=us-central1 \
    --set-env-vars="SUPABASE_URL=your-supabase-url,SUPABASE_KEY=your-supabase-key,GOOGLE_CLIENT_ID=your-google-client-id,GOOGLE_CLIENT_SECRET=your-google-client-secret,JWT_SECRET_KEY=your-jwt-secret,GOOGLE_API_KEY=your-google-ai-key"
```

## Configuration

### Environment Variables

Set these environment variables for your deployment:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# JWT Configuration
JWT_SECRET_KEY=your-secure-jwt-secret

# Google Generative AI
GOOGLE_API_KEY=your-google-ai-key
```

### Required Google Cloud APIs

Enable these APIs in your Google Cloud project:

1. **Cloud Build API** (`cloudbuild.googleapis.com`)
   - **Purpose**: Building and deploying Docker containers
   - **Required for**: Automated deployment process

2. **Cloud Run Admin API** (`run.googleapis.com`)
   - **Purpose**: Managing Cloud Run services
   - **Required for**: Deploying and managing the application

3. **Container Registry API** (`containerregistry.googleapis.com`)
   - **Purpose**: Storing and managing Docker images
   - **Required for**: Image storage and retrieval

### External API Requirements

1. **Google Generative AI API**
   - **Purpose**: AI-powered text comparison
   - **Model**: Gemma-3n-e4b-it
   - **Setup**: Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **Usage**: Advanced text analysis and comparison

2. **Supabase API**
   - **Purpose**: Database and user management
   - **Setup**: Create project at [supabase.com](https://supabase.com)
   - **Usage**: User authentication, activity tracking, data persistence

3. **Google OAuth API**
   - **Purpose**: User authentication
   - **Setup**: Configure OAuth credentials in [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - **Usage**: Secure user login and session management

4. **HuggingFace Datasets API**
   - **Purpose**: RACE dataset access
   - **Authentication**: Not required (public dataset)
   - **Usage**: Random text generation for testing

### CORS Configuration

Update the CORS origins in `main.py` for your production domain:

```python
allow_origins=[
    "http://localhost:3000",
    "https://your-production-domain.com",
    "https://www.your-production-domain.com"
]
```

## Monitoring and Maintenance

### Health Checks

- **Basic Health**: `GET /`
- **Detailed Health**: `GET /health`

### Viewing Logs

```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=lexidrom" --limit=50

# Follow logs in real-time
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=lexidrom"
```

### Performance Monitoring

Monitor your service in the [Google Cloud Console](https://console.cloud.google.com/run/detail/us-central1/lexidrom/metrics)

### Scaling Configuration

The default configuration includes:
- **Memory**: 2GB
- **CPU**: 2 vCPUs
- **Max Instances**: 10
- **Concurrency**: 80 requests per instance
- **Timeout**: 300 seconds

To adjust scaling:

```bash
gcloud run services update lexidrom \
    --region=us-central1 \
    --max-instances=20 \
    --memory=4Gi \
    --cpu=4
```

## Troubleshooting

### Authentication Consent Issues

If you encounter the error "https://www.googleapis.com/auth/cloud-platform scope is required but not consented":

1. **Clear all existing credentials**:
   ```bash
   gcloud auth revoke --all
   ```

2. **Login with no browser (recommended for this issue)**:
   ```bash
   gcloud auth application-default login --no-browser
   ```

3. **Follow the manual authentication steps**:
   - Copy the URL provided in the terminal
   - Open it in your browser
   - **Important**: Make sure to check all the required scopes, especially:
     - `https://www.googleapis.com/auth/cloud-platform`
     - `https://www.googleapis.com/auth/userinfo.email`
     - `https://www.googleapis.com/auth/sqlservice.login`
   - Complete the authentication process
   - Copy the authorization code back to the terminal

4. **Verify authentication**:
   ```bash
   gcloud auth list
   gcloud config list
   ```

### Installation Issues

1. **Google Cloud SDK Installation Problems**
   - **Windows**: If winget fails, download manually from [cloud.google.com/sdk/docs/install#windows](https://cloud.google.com/sdk/docs/install#windows)
   - **Permission Issues**: Run PowerShell as Administrator
   - **Path Issues**: Ensure the SDK is added to your PATH environment variable

2. **Authentication Issues**
   - **Clear existing credentials**: `gcloud auth revoke --all`
   - **Re-authenticate**: `gcloud auth login`
   - **Set application default**: `gcloud auth application-default login`
   - **If consent error occurs**: Run `gcloud auth application-default login --no-browser` and follow the manual authentication steps
   - **Ensure proper scopes**: Make sure to consent to all required scopes including `https://www.googleapis.com/auth/cloud-platform`

### Deployment Issues

1. **Build Failures**
   - Check `requirements.txt` for compatibility
   - Verify Dockerfile syntax
   - Check for missing dependencies

2. **Runtime Errors**
   - Verify environment variables are set
   - Check service logs for detailed error messages
   - Ensure all required services are accessible

3. **Performance Issues**
   - Increase memory allocation if needed
   - Optimize code for cold starts
   - Consider using min instances

4. **Authentication Issues**
   - Verify Google OAuth credentials
   - Check JWT secret key configuration
   - Ensure CORS settings are correct

### Debug Commands

```bash
# Check service status
gcloud run services describe lexidrom --region=us-central1

# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=lexidrom" --limit=10

# Test the service
curl https://your-service-url/

# Check environment variables
gcloud run services describe lexidrom --region=us-central1 --format="value(spec.template.spec.containers[0].env)"
```

## Security Considerations

1. **Environment Variables**: Store sensitive data in Google Secret Manager
2. **Authentication**: Implement proper authentication for production
3. **CORS**: Update CORS settings for your production domain
4. **HTTPS**: Cloud Run automatically provides HTTPS
5. **Input Validation**: All inputs are validated using Pydantic schemas

## Cost Optimization

1. **Use min instances**: Set minimum instances to reduce cold starts
2. **Optimize memory**: Right-size memory allocation
3. **Monitor usage**: Use Cloud Monitoring to track costs
4. **Set budgets**: Configure billing alerts

## Rollback Plan

If deployment fails or issues arise:

1. **Immediate Rollback**
```bash
# Deploy previous version
gcloud run services update-traffic lexidrom \
    --region=us-central1 \
    --to-revisions=REVISION_NAME=100
```

2. **Debug and Fix**
- Check logs for errors
- Test locally with same configuration
- Fix issues and redeploy

3. **Monitor**
- Watch metrics closely after deployment
- Set up alerts for critical issues
- Have rollback plan ready

## Support

For issues with:
- **Google Cloud**: Check [Cloud Run documentation](https://cloud.google.com/run/docs)
- **Application**: Check the logs and application code
- **Deployment**: Verify your project configuration and permissions

## Next Steps

1. Set up a custom domain
2. Configure SSL certificates
3. Set up monitoring and alerting
4. Implement CI/CD pipeline
5. Set up backup and disaster recovery 
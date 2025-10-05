# Bluesky Summarizer

A Flask-based web service that collects posts from Bluesky on a given topic and generates AI-powered summaries using Google's Gemini API.

## 🚀 Features

- **Topic-based Search**: Search for posts on Bluesky using any topic or keyword
- **AI-Powered Summaries**: Generate intelligent summaries using Google's Gemini 2.0 Flash model
- **RESTful API**: Simple HTTP endpoints for easy integration
- **Retry Logic**: Robust error handling with automatic retries for AI calls
- **CORS Support**: Ready for web application integration
- **Docker Support**: Containerized deployment ready
- **Fly.io Integration**: Production deployment configuration included

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Bluesky account credentials
- Google Gemini API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bluesky-summarizer
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Set up environment variables**
   
   Create a `.env` file or set the following environment variables:
   ```bash
   export GENAIKEY="your-google-gemini-api-key"
   export BSKYLOGIN="your-bluesky-username"
   export BSKYPASS="your-bluesky-password"
   ```

   **On Windows (PowerShell):**
   ```powershell
   $env:GENAIKEY="your-google-gemini-api-key"
   $env:BSKYLOGIN="your-bluesky-username"
   $env:BSKYPASS="your-bluesky-password"
   ```

4. **Run the application**
   ```bash
   poetry run flask --app app run
   ```

   **On Windows:**
   ```powershell
   py -m flask --app app run
   ```

The application will be available at `http://localhost:5000`

## 📖 API Documentation

### Get Topic Summary

**Endpoint:** `GET /summary/<topic>`

**Description:** Retrieves recent posts about a specific topic from Bluesky and generates an AI summary.

**Parameters:**
- `topic` (path parameter): The topic to search for (URL-encoded)

**Example Request:**
```bash
curl "http://localhost:5000/summary/Elon%20Musk"
```

**Example Response:**
```json
{
  "topic": "Elon Musk",
  "summary": "Recent posts about Elon Musk discuss his latest ventures in space technology and social media activities..."
}
```

## 🧪 Testing

Run the test suite:
```bash
poetry run python -m pytest test/
```

Or run with unittest:
```bash
poetry run python -m unittest test.test_app
```

## 🐳 Docker Deployment

### Build and Run Locally
```bash
docker build -t bluesky-summarizer .
docker run -p 8080:8080 \
  -e GENAIKEY="your-api-key" \
  -e BSKYLOGIN="your-username" \
  -e BSKYPASS="your-password" \
  bluesky-summarizer
```

### Deploy to Fly.io

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Deploy**
   ```bash
   fly deploy
   ```

3. **Set environment variables**
   ```bash
   fly secrets set GENAIKEY="your-api-key"
   fly secrets set BSKYLOGIN="your-username"
   fly secrets set BSKYPASS="your-password"
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GENAIKEY` | Google Gemini API key | Yes |
| `BSKYLOGIN` | Bluesky username/handle | Yes |
| `BSKYPASS` | Bluesky password | Yes |

### API Keys Setup

1. **Google Gemini API Key**: 
   - Visit [Google AI Studio](https://ai.google.dev/gemini-api/docs/quickstart)
   - Create a new API key
   - Set the `GENAIKEY` environment variable

2. **Bluesky Credentials**:
   - Use your Bluesky handle (e.g., `user.bsky.social`)
   - Use your account password or app-specific password

## 🏗️ Architecture

The application consists of:

- **PostSummarizer Class**: Core logic for fetching posts and generating summaries
- **Flask API**: RESTful endpoints for web service functionality
- **Retry Logic**: Automatic retry mechanism for API calls
- **Mock Support**: Dependency injection for testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 👥 Authors

- **Stasiu and Marek** - Initial work

## 🔮 Roadmap

- [ ] Implement daily scheduled summaries
- [ ] Add email notification system
- [ ] Support for multiple social media platforms
- [ ] Enhanced filtering and date range selection
- [ ] User authentication and personalized topics
- [ ] Data persistence and historical summaries
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
- uv (for building and dependency management)
- Bluesky account credentials
- Google Gemini API key
- Database on Turso

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bluesky-summarizer
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root with your API credentials:
   ```bash
   GENAIKEY=your-google-gemini-api-key
   BSKYLOGIN=your-bluesky-username
   BSKYPASS=your-bluesky-password
   SENDER_EMAIL=your-sender-email@example.com
   MJ_APIKEY_PUBLIC=your-mailjet-public-key
   MJ_APIKEY_PRIVATE=your-mailjet-private-key
   ```
   
   > **Note**: The `.env` file is automatically ignored by git to keep your credentials secure.

4. **Run the application**
   ```bash
   uv run python bluesky_summarizer.py
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
uv run pytest
```

## 🐳 Docker Deployment

### Build and Run Locally
```bash
docker build -t bluesky-summarizer .
docker run -p 8080:8080 \
  --env-file .env \
  bluesky-summarizer
```

Or with individual environment variables:
```bash
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
    fly secrets set SENDER_EMAIL="your-sender-email@example.com"
    fly secrets set MJ_APIKEY_PUBLIC="your-mailjet-public-key"
    fly secrets set MJ_APIKEY_PRIVATE="your-mailjet-private-key"
    ```

## 🔧 Configuration

All configuration is handled through a `.env` file in the project root. The application automatically loads these values on startup.

### Required Environment Variables

Create a `.env` file with the following variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `GENAIKEY` | Google Gemini API key | `AIzaSyC...` |
| `BSKYLOGIN` | Bluesky username/handle | `user.bsky.social` |
| `BSKYPASS` | Bluesky password | `your-password` |
| `SENDER_EMAIL` | Email address for sending notifications | `noreply@example.com` |
| `MJ_APIKEY_PUBLIC` | MailJet public API key | `your-public-key` |
| `MJ_APIKEY_PRIVATE` | MailJet private API key | `your-private-key` |

### API Keys Setup

1. **Google Gemini API Key**: 
   - Visit [Google AI Studio](https://ai.google.dev/gemini-api/docs/quickstart)
   - Create a new API key
   - Add it to your `.env` file as `GENAIKEY`

2. **Bluesky Credentials**:
   - Use your Bluesky handle (e.g., `user.bsky.social`)
   - Use your account password or app-specific password
   - Add them to your `.env` file as `BSKYLOGIN` and `BSKYPASS`

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

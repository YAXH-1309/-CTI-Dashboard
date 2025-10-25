# CTI Dashboard - Cyber Threat Intelligence Platform

A comprehensive real-time threat intelligence dashboard that aggregates and visualizes threat data from multiple sources including VirusTotal and AbuseIPDB.

## Features

### 🎯 Core Functionality
- **Real-time Threat Intelligence**: Aggregates data from VirusTotal and AbuseIPDB APIs
- **IOC Management**: Store and track IPs, domains, URLs, and file hashes
- **Threat Lookup**: Interactive lookup tool for IOC verification
- **Visualization Dashboard**: Real-time charts and metrics
- **Tagging System**: Categorize IOCs (phishing, malware, botnet, C2)
- **Export Capabilities**: Export data to CSV/JSON formats

### 📊 Dashboard Components
- Overall threat level indicator
- Threat trends over time
- Classification breakdown (Critical/High/Medium/Low/Clean)
- Geographic distribution of threats
- Top malicious IPs/domains
- Real-time statistics

### 🔍 Threat Intelligence Sources
- **VirusTotal API**: Domain and IP reputation checks
- **AbuseIPDB API**: IP abuse confidence scoring
- Extensible architecture for additional sources

## Installation

### Prerequisites
- Python 3.8+
- MongoDB 4.0+
- VirusTotal API key (free tier)
- AbuseIPDB API key (free tier)

### Setup Steps

1. **Clone and Setup Environment**
```bash
git clone <repository-url>
cd cti-dashboard
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment Variables**
```bash
cp .env.example .env
```

Edit `.env` file with your API keys:
```
VIRUSTOTAL_API_KEY=your_virustotal_api_key_here
ABUSEIPDB_API_KEY=your_abuseipdb_api_key_here
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=cti_dashboard
FLASK_ENV=development
FLASK_DEBUG=True
```

3. **Start MongoDB**
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or install MongoDB locally
# Follow instructions at: https://docs.mongodb.com/manual/installation/
```

4. **Run the Application**
```bash
python app.py
```

The dashboard will be available at `http://localhost:5000`

## API Endpoints

### Core Endpoints
- `GET /` - Main dashboard interface
- `POST /api/fetch-feeds` - Manually trigger feed updates
- `POST /api/lookup` - Lookup IOC against threat databases
- `GET /api/visuals/dashboard` - Get dashboard metrics
- `GET /api/visuals/trends` - Get threat trends data

### IOC Management
- `GET /api/iocs` - Get paginated IOCs with search/filter
- `POST /api/iocs/<id>/tag` - Update IOC tags
- `GET /api/export` - Export IOCs in JSON/CSV format

## Usage Examples

### Threat Lookup
```bash
curl -X POST http://localhost:5000/api/lookup \
  -H "Content-Type: application/json" \
  -d '{"ioc": "8.8.8.8", "type": "ip"}'
```

### Export Data
```bash
curl "http://localhost:5000/api/export?days=30&format=json" > threats.json
```

## Architecture

### Backend Components
- **Flask Application** (`app.py`): Main web server and API routes
- **Database Service** (`services/database.py`): MongoDB operations and data management
- **Threat Intel Service** (`services/threat_intel.py`): API integrations and IOC lookups
- **Visualization Service** (`services/visualization.py`): Dashboard metrics and chart data

### Frontend Components
- **Bootstrap 5**: Responsive UI framework
- **Chart.js**: Interactive charts and visualizations
- **Single Page Application**: Dynamic content loading without page refreshes

### Data Flow
1. **Background Scheduler**: Automatically fetches threat feeds every hour
2. **API Integration**: Real-time lookups against VirusTotal and AbuseIPDB
3. **Data Normalization**: Unified threat scoring across different sources
4. **Caching**: Prevents redundant API calls with 1-hour cache
5. **Visualization**: Real-time dashboard updates

## Configuration

### API Rate Limits
- **VirusTotal Free Tier**: 4 requests/minute
- **AbuseIPDB Free Tier**: 1000 requests/day

The application automatically handles rate limiting with appropriate delays.

### Threat Score Normalization
All threat scores are normalized to a 0-100 scale:
- **0-29**: Clean/Low risk
- **30-59**: Medium risk  
- **60-79**: High risk
- **80-100**: Critical risk

### Database Schema
```javascript
// IOC Document Structure
{
  "_id": ObjectId,
  "value": "192.168.1.1",
  "type": "ip",
  "threat_score": 85,
  "classification": "critical",
  "sources": ["virustotal", "abuseipdb"],
  "source_details": [...],
  "tags": ["malware", "botnet"],
  "timestamp": ISODate,
  "last_seen": ISODate,
  "description": "IP: 192.168.1.1"
}
```

## Extending the Platform

### Adding New Threat Intel Sources
1. Create new lookup methods in `ThreatIntelService`
2. Implement score normalization for the new source
3. Update the `lookup_ioc` method to include the new source
4. Add source-specific configuration to environment variables

### Custom Visualizations
1. Add new chart components in the dashboard template
2. Create corresponding data endpoints in `VisualizationService`
3. Implement frontend JavaScript for chart rendering

## Security Considerations

- **API Key Protection**: Store API keys in environment variables
- **Input Validation**: All IOC inputs are validated before processing
- **Rate Limiting**: Respects API provider rate limits
- **Data Sanitization**: MongoDB queries use parameterized inputs

## Troubleshooting

### Common Issues
1. **MongoDB Connection**: Ensure MongoDB is running on the configured port
2. **API Keys**: Verify API keys are valid and have sufficient quota
3. **Rate Limits**: Check API usage if lookups are failing
4. **Dependencies**: Ensure all Python packages are installed correctly

### Logs and Debugging
- Enable Flask debug mode in `.env` file
- Check console output for API errors
- Monitor MongoDB logs for database issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- VirusTotal for threat intelligence API
- AbuseIPDB for IP reputation data
- MongoDB for flexible data storage
- Flask and Bootstrap for web framework
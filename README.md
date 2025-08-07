# MLB Odds Feed - Unabated API v2.0

A Python script that fetches MLB odds from the Unabated API v2.0, including spread (run line), moneyline, and total (over/under) odds from all available sportsbooks.

## Features

- **Official Unabated API v2.0**: Uses the official partner API endpoints
- **Comprehensive Coverage**: Fetches odds from all major sportsbooks supported by Unabated
- **Multiple Market Types**: Includes spread/run line, moneyline, and total odds
- **Real-time Data**: Access to live odds with minimal latency
- **Robust Error Handling**: Built-in retry logic and error recovery
- **Structured JSON Output**: Clean, consistent JSON feed format
- **Game Status Tracking**: Includes live scores, game clock, and status updates

## Supported Sportsbooks

- Pinnacle
- Circa
- FanDuel
- DraftKings
- BetMGM
- Bovada
- BetOnline
- Bookmaker
- BetRivers
- Caesars
- PointsBet
- WynnBET

## Installation

1. **Clone or download** the project files to your local machine

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Your API key is already configured** in `config.py` and ready to use

## Usage

### Option 1: Web Server (Recommended) 🌐

Start the web server to access your feed via URLs:

```bash
# Quick start
./start_server.sh

# Or manually
python web_server.py
```

**Your feed URLs:**
- **📊 Main Feed**: `http://localhost:5000/feed`
- **📊 Pretty JSON**: `http://localhost:5000/feed?pretty=true`
- **📈 API Status**: `http://localhost:5000/status`
- **🏠 Documentation**: `http://localhost:5000/`

**Features:**
- ⚡ Real-time MLB odds from 65+ sportsbooks
- 🔄 Smart caching (updates every 5 minutes)
- 🌍 CORS enabled for web applications
- 📱 Mobile-friendly JSON format

### Option 2: Command Line 💻

Run the script directly for console output:

```bash
python mlb_odds_feed.py
```

## Configuration

### API Settings (`config.py`)

The script uses the official Unabated API v2.0 endpoints:

```python
API_CONFIG = {
    'base_url': 'https://partner-api.unabated.com',
    'endpoints': {
        'game_odds_snapshot': '/v2/markets/gameOdds',
        'game_odds_changes': '/v2/markets/changes',
        'market_sources': '/v2/marketSources',
        'teams': '/v2/teams',
        # ... other endpoints
    }
}
```

The API uses `x-api-key` parameter authentication as specified in the official documentation.

### Output Settings

Customize output behavior:

```python
OUTPUT_CONFIG = {
    'pretty_print': True,        # Format JSON output with indentation
    'save_to_file': True,        # Save output to file
    'file_prefix': 'mlb_odds_',  # Prefix for output files
    'include_metadata': True     # Include feed metadata
}
```

## Usage

### Basic Usage

Run the script to fetch today's MLB odds:

```bash
python mlb_odds_feed.py
```

This will:
1. Fetch odds data from the Unabated API
2. Process and structure the data
3. Output JSON to console
4. Save to a timestamped file (if configured)

### Output Format

The script generates a JSON feed with the following structure:

```json
{
  "feed_info": {
    "title": "MLB Odds Feed - Unabated API",
    "description": "Today's MLB odds including spread, moneyline, and totals from all available sportsbooks",
    "generated_at": "2025-01-16T20:30:00.000Z",
    "source": "Unabated API",
    "total_games": 2,
    "supported_sportsbooks": [...],
    "market_types": ["spread", "moneyline", "total"]
  },
  "games": [
    {
      "game_id": "mlb_2025_01_16_yankees_redsox",
      "event_name": "New York Yankees at Boston Red Sox",
      "game_time": "2025-01-16T19:10:00Z",
      "away_team": "New York Yankees",
      "home_team": "Boston Red Sox",
      "status": "scheduled",
      "odds": {
        "spread": [...],
        "moneyline": [...],
        "total": [...]
      }
    }
  ]
}
```

See `sample_output.json` for a complete example.

## Error Handling

The script includes comprehensive error handling:

- **Network Issues**: Automatic retry with exponential backoff
- **Authentication Errors**: Clear error messages for API key issues
- **Rate Limiting**: Automatic handling of rate limit responses
- **Data Processing**: Flexible parsing to handle different API response structures
- **Graceful Degradation**: Returns error feeds when data cannot be fetched

## API Endpoint Flexibility

Since the exact Unabated API endpoints are not publicly documented, the script tries multiple possible endpoint structures:

- `/v1/odds/mlb`
- `/v1/sports/mlb/odds`
- `/api/v1/mlb/odds`
- `/odds/mlb`

This approach maximizes the chance of successful connection once you have access to the actual API documentation.

## Logging

The script provides detailed logging to help with debugging:

- **INFO**: General operation status
- **WARNING**: Non-critical issues (missing data, retries)
- **ERROR**: Critical errors that prevent operation
- **DEBUG**: Detailed request/response information

## Customization

### Adding New Sportsbooks

Update the `SUPPORTED_SPORTSBOOKS` list in `config.py`:

```python
SUPPORTED_SPORTSBOOKS = [
    'Pinnacle',
    'NewSportsbook',  # Add new sportsbook here
    # ... existing sportsbooks
]
```

### Adding New Market Types

Update the `MARKET_TYPES` list in `config.py`:

```python
MARKET_TYPES = ['spread', 'moneyline', 'total', 'player_props']  # Add new market type
```

Then update the processing logic in the `_process_market_odds` method.

## Troubleshooting

### Common Issues

1. **Authentication Errors (401)**:
   - Verify your API key is correct
   - Check if the API key has the necessary permissions

2. **Endpoint Not Found (404)**:
   - Update the API endpoints in `config.py` with actual Unabated endpoints
   - Contact Unabated support for API documentation

3. **No Data Returned**:
   - Check if there are MLB games scheduled for today
   - Verify the date format matches API expectations

4. **Rate Limiting (429)**:
   - The script automatically handles rate limits with backoff
   - Consider reducing request frequency if issues persist

### Debug Mode

Enable debug logging by updating `config.py`:

```python
LOGGING_CONFIG = {
    'level': 'DEBUG',  # Change from 'INFO' to 'DEBUG'
    # ... other settings
}
```

## Important Notes

1. **Official API**: This script uses the official Unabated Partner API v2.0 with correct endpoints and authentication.

2. **API Key Security**: Your API key is configured in `config.py`. In production environments, consider loading it from environment variables.

3. **Rate Limits**: The Unabated API documentation recommends not calling endpoints more than once per second. The script includes appropriate retry logic.

4. **Data Structure**: The script correctly parses the complex Unabated API response structure including market sources, teams, and game odds events.

5. **Data Accuracy**: Always verify odds data before making any betting decisions. This tool is for informational purposes only.

## Support

For issues related to:
- **Script functionality**: Check the logs and troubleshooting section
- **API access**: Contact Unabated support for API documentation and endpoint details
- **Data accuracy**: Verify with Unabated's official platform

## License

This project is for educational and informational purposes only. Please ensure compliance with Unabated's API terms of service.

## Disclaimer

This tool is for informational purposes only. Always verify odds data independently before making any betting decisions. The authors are not responsible for any losses incurred from using this tool.
"""
Configuration settings for the MLB Odds Feed

This file contains API configuration and settings that can be easily
modified without changing the main application code.
"""

# API Configuration
UNABATED_API_KEY = "92329d16391c4bc9af0684676fb3d83d"

# API Endpoints (based on official Unabated API documentation v2.0)
API_CONFIG = {
    'base_url': 'https://partner-api.unabated.com',
    'endpoints': {
        'game_odds_snapshot': '/v2/markets/gameOdds',
        'game_odds_changes': '/v2/markets/changes',
        'player_props_snapshot': '/v2/markets/playerProps',
        'player_props_changes': '/v2/markets/playerProps/changes',
        'bet_types': '/v2/betTypes',
        'market_sources': '/v2/marketSources',
        'teams': '/v2/teams',
        'players': '/v2/players',
        'upcoming_events': '/v2/events/upcoming'
    },
    'timeout': 30,
    'max_retries': 3
}

# Sportsbooks to include (based on Unabated's supported books)
SUPPORTED_SPORTSBOOKS = [
    'Pinnacle',
    'Circa',
    'FanDuel', 
    'DraftKings',
    'BetMGM',
    'Bovada',
    'BetOnline',
    'Bookmaker',
    'BetRivers',
    'Caesars',
    'PointsBet',
    'WynnBET'
]

# Market types to fetch
MARKET_TYPES = ['spread', 'moneyline', 'total']

# Output settings
OUTPUT_CONFIG = {
    'pretty_print': True,
    'save_to_file': True,
    'file_prefix': 'mlb_odds_',
    'include_metadata': True
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_logging': False,
    'log_file': 'mlb_odds_feed.log'
}
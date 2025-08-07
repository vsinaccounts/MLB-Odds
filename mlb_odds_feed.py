#!/usr/bin/env python3
"""
MLB Odds Feed from Unabated API

This script fetches today's MLB odds from the Unabated API, including:
- Spread odds
- Moneyline odds  
- Total (over/under) odds
From all available sportsbooks.

Usage:
    python mlb_odds_feed.py

Output:
    JSON feed with structured odds data

Note: This script uses placeholder API endpoints. You'll need to update
the endpoints in config.py with the actual Unabated API endpoints
once you have access to their documentation.
"""

import json
import requests
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import logging
import time
from config import (
    UNABATED_API_KEY, 
    API_CONFIG, 
    SUPPORTED_SPORTSBOOKS, 
    MARKET_TYPES, 
    OUTPUT_CONFIG,
    LOGGING_CONFIG
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)

class UnabatedMLBOddsFeed:
    """Fetches MLB odds from Unabated API and formats them into a JSON feed."""
    
    def __init__(self, api_key: str):
        """
        Initialize the odds feed with API credentials.
        
        Args:
            api_key: Unabated API key
        """
        self.api_key = api_key
        self.base_url = API_CONFIG['base_url']
        self.timeout = API_CONFIG['timeout']
        self.max_retries = API_CONFIG['max_retries']
        
        # Unabated uses x-api-key parameter for authentication (not header)
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "MLB-Odds-Feed/2.0"
        }
        
        # MLB League ID from documentation
        self.MLB_LEAGUE_ID = 5
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request with retry logic using Unabated API structure.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response data or None if error
        """
        # Add API key to params (Unabated uses x-api-key parameter)
        if params is None:
            params = {}
        params['x-api-key'] = self.api_key
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    params=params, 
                    timeout=self.timeout
                )
                
                # Log the request for debugging (hide API key)
                safe_url = response.url.replace(self.api_key, "***API_KEY***")
                logger.debug(f"Request: {safe_url}")
                logger.debug(f"Status: {response.status_code}")
                
                if response.status_code == 401:
                    logger.error("Authentication failed - check API key")
                    return None
                elif response.status_code == 403:
                    logger.error("Access forbidden - check API permissions")
                    return None
                elif response.status_code == 429:
                    logger.warning("Rate limit exceeded, waiting...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return None
        
        logger.error(f"Failed to complete request after {self.max_retries} attempts")
        return None
        
    def fetch_game_odds_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Fetch complete snapshot of current game odds from Unabated API.
        
        Returns:
            Complete odds data or None if error
        """
        logger.info("Fetching game odds snapshot from Unabated API...")
        
        endpoint = API_CONFIG['endpoints']['game_odds_snapshot']
        data = self._make_request(endpoint)
        
        if data is not None:
            logger.info("Successfully fetched game odds snapshot")
            logger.debug(f"API Response keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            return data
        
        logger.error("Failed to fetch game odds snapshot")
        return None
    
    def get_mlb_market_sources(self) -> Optional[Dict[str, Any]]:
        """
        Get list of all market sources (sportsbooks) available.
        
        Returns:
            Market sources data or None if error
        """
        logger.info("Fetching market sources...")
        
        endpoint = API_CONFIG['endpoints']['market_sources']
        data = self._make_request(endpoint)
        
        if data is not None:
            logger.info(f"Successfully fetched {len(data)} market sources")
            return data
        
        return None
    
    def process_unabated_odds_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process Unabated API odds data into structured format.
        Based on official Unabated API documentation v2.0.
        
        Args:
            raw_data: Raw response from Unabated gameOdds API
            
        Returns:
            List of structured game data
        """
        processed_games = []
        
        try:
            # Get market sources for sportsbook names
            market_sources = {}
            if 'marketSources' in raw_data and isinstance(raw_data['marketSources'], list):
                logger.debug(f"Found {len(raw_data['marketSources'])} market sources")
                for source in raw_data['marketSources']:
                    if isinstance(source, dict) and 'id' in source and 'name' in source:
                        market_sources[source['id']] = source['name']
            else:
                logger.debug(f"Market sources data structure: {type(raw_data.get('marketSources', 'Not found'))}")
            
            # Get teams data
            teams = {}
            if 'teams' in raw_data and isinstance(raw_data['teams'], list):
                logger.debug(f"Found {len(raw_data['teams'])} teams")
                for team in raw_data['teams']:
                    if isinstance(team, dict) and 'id' in team:
                        teams[team['id']] = team
                        # Log a few sample teams to see the structure
                        if len(teams) <= 3:
                            logger.debug(f"Sample team data: ID={team['id']}, Name={team.get('name', 'No name')}, Abbr={team.get('abbreviation', 'No abbr')}")
            else:
                logger.debug(f"Teams data structure: {type(raw_data.get('teams', 'Not found'))}")
            
            # Process game odds events
            if 'gameOddsEvents' not in raw_data:
                logger.warning("No gameOddsEvents found in API response")
                return processed_games
            
            logger.debug(f"gameOddsEvents keys: {list(raw_data['gameOddsEvents'].keys())}")
            
            # MLB events are under lg5 (League ID 5 = MLB)
            mlb_keys = [key for key in raw_data['gameOddsEvents'].keys() if key.startswith('lg5:')]
            logger.debug(f"Found MLB keys: {mlb_keys}")
            
            for key in mlb_keys:
                events = raw_data['gameOddsEvents'][key]
                logger.debug(f"Processing {len(events)} events for key {key}")
                for event in events:
                    processed_game = self._process_unabated_event(event, market_sources, teams)
                    if processed_game:
                        processed_games.append(processed_game)
            
            logger.info(f"Processed {len(processed_games)} MLB games from Unabated API")
            return processed_games
            
        except Exception as e:
            logger.error(f"Error in process_unabated_odds_data: {e}", exc_info=True)
            return []
    
    def _process_unabated_event(self, event_data: Dict[str, Any], market_sources: Dict[int, str], teams: Dict[int, Dict]) -> Optional[Dict[str, Any]]:
        """
        Process a single Unabated event into structured format.
        Based on official Unabated API documentation v2.0.
        
        Args:
            event_data: Raw event data from Unabated API
            market_sources: Dictionary of market source ID to name mappings
            teams: Dictionary of team ID to team data mappings
            
        Returns:
            Structured game data or None if processing fails
        """
        try:
            event_id = event_data.get('eventId')
            if not event_id:
                logger.warning("Event missing eventId")
                return None
            
            # Extract team information
            event_teams = event_data.get('eventTeams', {})
            away_team_data = event_teams.get('0')  # Away team (side 0)
            home_team_data = event_teams.get('1')  # Home team (side 1)
            
            if not away_team_data or not home_team_data:
                logger.warning(f"Event {event_id} missing team data")
                return None
            
            # Get team names from teams data
            away_team_id = away_team_data.get('id')
            home_team_id = home_team_data.get('id')
            
            logger.debug(f"Looking up teams: Away ID={away_team_id}, Home ID={home_team_id}")
            
            away_team_info = teams.get(away_team_id, {})
            home_team_info = teams.get(home_team_id, {})
            
            away_team_name = away_team_info.get('name', f'Team {away_team_id}')
            home_team_name = home_team_info.get('name', f'Team {home_team_id}')
            
            logger.debug(f"Resolved team names: {away_team_name} at {home_team_name}")
            
            # Create basic game structure
            processed_game = {
                'game_id': str(event_id),
                'event_name': f"{away_team_name} at {home_team_name}",
                'game_time': event_data.get('eventStart'),
                'away_team': away_team_name,
                'home_team': home_team_name,
                'status': self._get_status_name(event_data.get('statusId', 1)),
                'away_score': away_team_data.get('score'),
                'home_score': home_team_data.get('score'),
                'game_clock': event_data.get('gameClock'),
                'odds': {
                    'spread': [],
                    'moneyline': [],
                    'total': []
                }
            }
            
            # Process market lines
            market_lines = event_data.get('gameOddsMarketSourcesLines', {})
            logger.debug(f"Event {event_id} has {len(market_lines)} market line groups")
            if len(market_lines) > 0:
                # Log first few market line keys for debugging
                sample_keys = list(market_lines.keys())[:3]
                logger.debug(f"Sample market line keys: {sample_keys}")
            self._process_unabated_market_lines(market_lines, market_sources, processed_game)
            
            return processed_game
            
        except Exception as e:
            logger.error(f"Error processing Unabated event: {e}")
            return None
    
    def _get_status_name(self, status_id: int) -> str:
        """Convert status ID to readable name."""
        status_map = {
            1: 'Pre-game',
            2: 'Live',
            3: 'Final',
            4: 'Delayed',
            5: 'Postponed',
            6: 'Cancelled'
        }
        return status_map.get(status_id, 'Unknown')
    
    def _process_unabated_market_lines(self, market_lines: Dict[str, Any], market_sources: Dict[int, str], processed_game: Dict[str, Any]):
        """
        Process Unabated market lines into structured odds format.
        Based on official Unabated API documentation v2.0.
        
        Args:
            market_lines: Market lines data from Unabated API
            market_sources: Dictionary of market source ID to name mappings
            processed_game: Game data structure to populate with odds
        """
        # Bet type mappings based on common MLB bet types
        bet_type_map = {
            1: 'moneyline',      # Moneyline
            2: 'spread',         # Point Spread (Run Line in MLB)
            3: 'total',          # Total Points (Over/Under)
        }
        
        # Process each market line key (format: si{side}:ms{market_source}:an{alternate})
        for line_key, bet_types in market_lines.items():
            try:
                # Parse the line key: si0:ms7:an0 -> side=0, market_source=7, alternate=0
                parts = line_key.split(':')
                if len(parts) != 3:
                    logger.debug(f"Skipping malformed line key: {line_key}")
                    continue
                
                side_id = int(parts[0][2:])  # Remove 'si' prefix
                market_source_id = int(parts[1][2:])  # Remove 'ms' prefix
                alternate_num = int(parts[2][2:])  # Remove 'an' prefix
                
                # Skip alternate lines for now (an0 is the main line)
                if alternate_num != 0:
                    continue
                
                # Get sportsbook name
                sportsbook_name = market_sources.get(market_source_id, f'Book_{market_source_id}')
                logger.debug(f"Processing line for {sportsbook_name} (ID: {market_source_id}), side: {side_id}")
                
                # Process each bet type for this line
                for bet_type_key, market_line_data in bet_types.items():
                    if not bet_type_key.startswith('bt'):
                        continue
                        
                    bet_type_id = int(bet_type_key[2:])  # Remove 'bt' prefix
                    market_type = bet_type_map.get(bet_type_id)
                    
                    logger.debug(f"  Bet type {bet_type_id} -> {market_type}, Price: {market_line_data.get('americanPrice')}, Points: {market_line_data.get('points')}")
                    
                    if not market_type:
                        logger.debug(f"  Unknown bet type ID: {bet_type_id}")
                        continue
                    
                    self._add_market_line_to_game(
                        processed_game, 
                        market_type, 
                        sportsbook_name, 
                        side_id, 
                        market_line_data
                    )
                    
            except (ValueError, KeyError, IndexError) as e:
                logger.debug(f"Error parsing market line key {line_key}: {e}")
                continue
    
    def _add_market_line_to_game(self, game: Dict[str, Any], market_type: str, sportsbook: str, side_id: int, line_data: Dict[str, Any]):
        """Add a single market line to the game odds structure."""
        try:
            if market_type == 'moneyline':
                # For moneyline, we need both sides to create a complete entry
                existing_entry = None
                for entry in game['odds']['moneyline']:
                    if entry['sportsbook'] == sportsbook:
                        existing_entry = entry
                        break
                
                if not existing_entry:
                    existing_entry = {
                        'sportsbook': sportsbook,
                        'away_team': {'odds': None},
                        'home_team': {'odds': None},
                        'last_updated': line_data.get('modifiedOn')
                    }
                    game['odds']['moneyline'].append(existing_entry)
                
                # side_id 0 = away, side_id 1 = home
                if side_id == 0:
                    existing_entry['away_team']['odds'] = line_data.get('americanPrice')
                else:
                    existing_entry['home_team']['odds'] = line_data.get('americanPrice')
            
            elif market_type == 'spread':
                # For spread, we need both sides to create a complete entry
                existing_entry = None
                for entry in game['odds']['spread']:
                    if entry['sportsbook'] == sportsbook:
                        existing_entry = entry
                        break
                
                if not existing_entry:
                    existing_entry = {
                        'sportsbook': sportsbook,
                        'away_team': {'spread': None, 'odds': None},
                        'home_team': {'spread': None, 'odds': None},
                        'last_updated': line_data.get('modifiedOn')
                    }
                    game['odds']['spread'].append(existing_entry)
                
                # side_id 0 = away, side_id 1 = home
                if side_id == 0:
                    existing_entry['away_team']['spread'] = line_data.get('points')
                    existing_entry['away_team']['odds'] = line_data.get('americanPrice')
                else:
                    existing_entry['home_team']['spread'] = line_data.get('points')
                    existing_entry['home_team']['odds'] = line_data.get('americanPrice')
            
            elif market_type == 'total':
                # For totals, we need both sides (over/under) to create a complete entry
                existing_entry = None
                for entry in game['odds']['total']:
                    if entry['sportsbook'] == sportsbook:
                        existing_entry = entry
                        break
                
                if not existing_entry:
                    existing_entry = {
                        'sportsbook': sportsbook,
                        'total': line_data.get('points'),
                        'over': {'odds': None},
                        'under': {'odds': None},
                        'last_updated': line_data.get('modifiedOn')
                    }
                    game['odds']['total'].append(existing_entry)
                
                # side_id 0 = over, side_id 1 = under for totals
                if side_id == 0:
                    existing_entry['over']['odds'] = line_data.get('americanPrice')
                else:
                    existing_entry['under']['odds'] = line_data.get('americanPrice')
                    
        except Exception as e:
            logger.debug(f"Error adding market line: {e}")
    
    def get_mlb_teams(self) -> Optional[Dict[int, Dict]]:
        """
        Get MLB team data with actual team names.
        
        Returns:
            Dictionary mapping team ID to team data
        """
        logger.info("Fetching MLB teams data...")
        
        endpoint = API_CONFIG['endpoints']['teams']
        params = {'leagues': '5'}  # MLB league ID
        data = self._make_request(endpoint, params)
        
        if data and isinstance(data, list):
            teams = {}
            for team in data:
                if isinstance(team, dict) and 'id' in team:
                    teams[team['id']] = team
            logger.info(f"Successfully fetched {len(teams)} MLB teams")
            return teams
        
        logger.warning("Failed to fetch MLB teams data")
        return None

    def generate_feed(self) -> Dict[str, Any]:
        """
        Generate the complete MLB odds feed using Unabated API v2.0.
        
        Returns:
            Complete JSON feed with all games and odds
        """
        logger.info("Starting MLB odds feed generation using Unabated API v2.0...")
        
        # Fetch MLB teams data first (for real team names)
        mlb_teams = self.get_mlb_teams()
        if not mlb_teams:
            logger.warning("Could not fetch MLB teams data, team names may not be accurate")
            mlb_teams = {}
        
        # Fetch complete game odds snapshot
        raw_odds_data = self.fetch_game_odds_snapshot()
        if not raw_odds_data:
            logger.error("No odds data found or error fetching data from Unabated API")
            return self._create_error_feed("No odds data found or error fetching data from Unabated API")
        
        # Override teams data with the accurate MLB teams data
        if mlb_teams:
            raw_odds_data['teams'] = list(mlb_teams.values())
        
        # Process the Unabated API data
        processed_games = self.process_unabated_odds_data(raw_odds_data)
        
        if not processed_games:
            logger.warning("No MLB games could be processed from the Unabated API response")
            return self._create_error_feed("No MLB games could be processed from the API response")
        
        # Get list of market sources for metadata
        market_sources_data = self.get_mlb_market_sources()
        available_sportsbooks = []
        if market_sources_data:
            available_sportsbooks = [source.get('name', 'Unknown') for source in market_sources_data if source.get('isActive', False)]
        
        # Create final feed structure
        feed = {
            'feed_info': {
                'title': 'MLB Odds Feed - Unabated API v2.0',
                'description': 'MLB odds including spread, moneyline, and totals from all available sportsbooks via Unabated',
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'source': 'Unabated API v2.0',
                'api_endpoint': f"{self.base_url}{API_CONFIG['endpoints']['game_odds_snapshot']}",
                'total_games': len(processed_games),
                'available_sportsbooks': available_sportsbooks,
                'market_types': ['spread', 'moneyline', 'total'],
                'league': 'MLB (League ID: 5)'
            },
            'games': processed_games
        }
        
        logger.info(f"Successfully generated feed with {len(processed_games)} MLB games")
        return feed
    
    def _create_error_feed(self, error_message: str) -> Dict[str, Any]:
        """Create an error feed structure."""
        return {
            'feed_info': {
                'title': 'MLB Odds Feed - Error',
                'description': 'Error occurred while fetching odds data',
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'source': 'Unabated API',
                'error': error_message,
                'total_games': 0
            },
            'games': []
        }

def main():
    """Main function to generate and output the MLB odds feed."""
    try:
        # Create odds feed instance
        odds_feed = UnabatedMLBOddsFeed(UNABATED_API_KEY)
        
        # Generate the feed
        feed_data = odds_feed.generate_feed()
        
        # Output JSON feed to console
        if OUTPUT_CONFIG['pretty_print']:
            print(json.dumps(feed_data, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(feed_data, ensure_ascii=False))
        
        # Optionally save to file
        if OUTPUT_CONFIG['save_to_file']:
            output_file = f"{OUTPUT_CONFIG['file_prefix']}{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                if OUTPUT_CONFIG['pretty_print']:
                    json.dump(feed_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(feed_data, f, ensure_ascii=False)
            
            logger.info(f"Feed saved to {output_file}")
        
        # Log summary
        games_count = feed_data.get('feed_info', {}).get('total_games', 0)
        logger.info(f"Feed generation completed with {games_count} games")
        
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        error_feed = {
            'feed_info': {
                'title': 'MLB Odds Feed - Critical Error',
                'description': 'Critical error occurred while generating feed',
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'source': 'Unabated API',
                'error': str(e),
                'total_games': 0
            },
            'games': []
        }
        print(json.dumps(error_feed, indent=2, ensure_ascii=False))
        return 1  # Exit with error code
    
    return 0  # Success

if __name__ == "__main__":
    main()
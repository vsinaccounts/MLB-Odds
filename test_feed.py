#!/usr/bin/env python3
"""
Test script for the MLB Odds Feed

This script creates a mock API response to test the feed processing logic
without making actual API calls. Useful for development and testing.
"""

import json
from datetime import datetime, timezone
from mlb_odds_feed import UnabatedMLBOddsFeed

def create_mock_api_response():
    """Create a mock API response matching Unabated API v2.0 structure."""
    return {
        "marketSources": [
            {"id": 1, "name": "DraftKings", "isActive": True},
            {"id": 2, "name": "FanDuel", "isActive": True}
        ],
        "teams": [
            {"id": 1, "name": "New York Yankees", "abbreviation": "NYY"},
            {"id": 2, "name": "Boston Red Sox", "abbreviation": "BOS"}
        ],
        "gameOddsEvents": {
            "lg5:pt1:pregame": [
                {
                    "eventId": 12345,
                    "eventStart": "2025-01-16T19:10:00Z",
                    "statusId": 1,
                    "eventTeams": {
                        "0": {"id": 1, "rotationNumber": 901, "score": None},  # Away team
                        "1": {"id": 2, "rotationNumber": 902, "score": None}   # Home team
                    },
                    "gameOddsMarketSourceLines": {
                        "si0:ms1:an0": {  # Away team, DraftKings
                            "bt1": {  # Moneyline
                                "americanPrice": -150,
                                "points": None,
                                "modifiedOn": "2025-01-16T20:25:00Z"
                            },
                            "bt2": {  # Spread
                                "americanPrice": -110,
                                "points": -1.5,
                                "modifiedOn": "2025-01-16T20:25:00Z"
                            },
                            "bt3": {  # Total Over
                                "americanPrice": -110,
                                "points": 8.5,
                                "modifiedOn": "2025-01-16T20:25:00Z"
                            }
                        },
                        "si1:ms1:an0": {  # Home team, DraftKings
                            "bt1": {  # Moneyline
                                "americanPrice": 130,
                                "points": None,
                                "modifiedOn": "2025-01-16T20:25:00Z"
                            },
                            "bt2": {  # Spread
                                "americanPrice": -110,
                                "points": 1.5,
                                "modifiedOn": "2025-01-16T20:25:00Z"
                            },
                            "bt3": {  # Total Under
                                "americanPrice": -110,
                                "points": 8.5,
                                "modifiedOn": "2025-01-16T20:25:00Z"
                            }
                        },
                        "si0:ms2:an0": {  # Away team, FanDuel
                            "bt1": {  # Moneyline
                                "americanPrice": -145,
                                "points": None,
                                "modifiedOn": "2025-01-16T20:28:00Z"
                            },
                            "bt2": {  # Spread
                                "americanPrice": -115,
                                "points": -1.5,
                                "modifiedOn": "2025-01-16T20:28:00Z"
                            },
                            "bt3": {  # Total Over
                                "americanPrice": -105,
                                "points": 8.5,
                                "modifiedOn": "2025-01-16T20:28:00Z"
                            }
                        },
                        "si1:ms2:an0": {  # Home team, FanDuel
                            "bt1": {  # Moneyline
                                "americanPrice": 125,
                                "points": None,
                                "modifiedOn": "2025-01-16T20:28:00Z"
                            },
                            "bt2": {  # Spread
                                "americanPrice": -105,
                                "points": 1.5,
                                "modifiedOn": "2025-01-16T20:28:00Z"
                            },
                            "bt3": {  # Total Under
                                "americanPrice": -115,
                                "points": 8.5,
                                "modifiedOn": "2025-01-16T20:28:00Z"
                            }
                        }
                    }
                }
            ]
        }
    }

def test_data_processing():
    """Test the data processing logic with mock data."""
    print("Testing MLB Odds Feed data processing...")
    
    # Create a feed instance (API key won't be used for this test)
    feed = UnabatedMLBOddsFeed("test_key")
    
    # Create mock data
    mock_data = create_mock_api_response()
    
    # Process the mock data
    processed_games = feed.process_unabated_odds_data(mock_data)
    
    # Create test feed
    test_feed = {
        'feed_info': {
            'title': 'MLB Odds Feed - Test Data',
            'description': 'Test feed with mock data',
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'source': 'Mock Data',
            'total_games': len(processed_games)
        },
        'games': processed_games
    }
    
    # Output the test feed
    print("\n" + "="*50)
    print("TEST FEED OUTPUT:")
    print("="*50)
    print(json.dumps(test_feed, indent=2, ensure_ascii=False))
    
    # Save test output
    with open('test_output.json', 'w', encoding='utf-8') as f:
        json.dump(test_feed, f, indent=2, ensure_ascii=False)
    
    print(f"\nTest completed successfully!")
    print(f"- Processed {len(processed_games)} games")
    print(f"- Test output saved to 'test_output.json'")
    
    # Validate structure
    if processed_games:
        game = processed_games[0]
        print(f"\nSample game structure validation:")
        print(f"- Game ID: {game.get('game_id')}")
        print(f"- Event: {game.get('event_name')}")
        print(f"- Spread odds count: {len(game.get('odds', {}).get('spread', []))}")
        print(f"- Moneyline odds count: {len(game.get('odds', {}).get('moneyline', []))}")
        print(f"- Total odds count: {len(game.get('odds', {}).get('total', []))}")

if __name__ == "__main__":
    test_data_processing()
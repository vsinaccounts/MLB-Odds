#!/usr/bin/env python3
"""
Simple Flask web server to serve MLB odds feed as a URL endpoint.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import logging
import os
from datetime import datetime
from mlb_odds_feed import UnabatedMLBOddsFeed
from config import UNABATED_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Cache for feed data (simple in-memory cache)
feed_cache = {
    'data': None,
    'last_updated': None,
    'cache_duration_minutes': 5  # Cache for 5 minutes
}

def get_cached_feed():
    """Get cached feed data or fetch new data if cache is expired."""
    now = datetime.now()
    
    # Check if cache is valid
    if (feed_cache['data'] is not None and 
        feed_cache['last_updated'] is not None and 
        (now - feed_cache['last_updated']).total_seconds() < feed_cache['cache_duration_minutes'] * 60):
        logger.info("Returning cached feed data")
        return feed_cache['data']
    
    # Fetch new data
    logger.info("Fetching fresh feed data from Unabated API")
    try:
        odds_feed = UnabatedMLBOddsFeed(UNABATED_API_KEY)
        feed_data = odds_feed.generate_feed()
        
        # Update cache
        feed_cache['data'] = feed_data
        feed_cache['last_updated'] = now
        
        logger.info(f"Successfully cached feed with {feed_data.get('feed_info', {}).get('total_games', 0)} games")
        return feed_data
        
    except Exception as e:
        logger.error(f"Error fetching feed data: {e}")
        # Return cached data if available, even if expired
        if feed_cache['data'] is not None:
            logger.warning("Returning expired cached data due to API error")
            return feed_cache['data']
        
        # Return error response
        return {
            'feed_info': {
                'title': 'MLB Odds Feed - Error',
                'description': 'Error fetching odds data',
                'generated_at': now.isoformat(),
                'source': 'Unabated API v2.0',
                'error': str(e),
                'total_games': 0
            },
            'games': []
        }

@app.route('/')
def home():
    """Serve the main odds display page."""
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>MLB Odds Feed API</h1>
        <p>Welcome to the MLB Odds Feed powered by Unabated API v2.0</p>
        
        <h2>Available Endpoints:</h2>
        <ul>
            <li><strong><a href="/feed">/feed</a></strong> - Complete MLB odds feed (JSON)</li>
            <li><strong><a href="/feed?pretty=true">/feed?pretty=true</a></strong> - Pretty-printed JSON</li>
            <li><strong><a href="/status">/status</a></strong> - API status and cache info</li>
            <li><strong><a href="/games/count">/games/count</a></strong> - Just the game count</li>
        </ul>
        
        <h2>Feed Information:</h2>
        <ul>
            <li><strong>Data Source:</strong> Unabated API v2.0</li>
            <li><strong>Update Frequency:</strong> Real-time with 5-minute caching</li>
            <li><strong>Markets:</strong> Spread, Moneyline, Totals</li>
            <li><strong>Sportsbooks:</strong> 65+ including FanDuel, DraftKings, BetMGM, Caesars</li>
        </ul>
        
        <p><em>Last updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC') + """</em></p>
        """

@app.route('/styles.css')
def serve_css():
    """Serve the CSS file."""
    return send_from_directory('.', 'styles.css', mimetype='text/css')

@app.route('/script.js')
def serve_js():
    """Serve the JavaScript file."""
    return send_from_directory('.', 'script.js', mimetype='application/javascript')

@app.route('/sample_output.json')
def serve_sample_data():
    """Serve the sample JSON data."""
    return send_from_directory('.', 'sample_output.json', mimetype='application/json')

@app.route('/test_output.json')
def serve_test_data():
    """Serve the test JSON data."""
    return send_from_directory('.', 'test_output.json', mimetype='application/json')

@app.route('/logos/<sportsbook>')
def serve_logo(sportsbook):
    """Serve sportsbook logos with fallback to generated SVG."""
    try:
        # URL decode the sportsbook name to handle spaces and special characters
        import urllib.parse
        decoded_sportsbook = urllib.parse.unquote(sportsbook)
        
        # First try to serve the file as requested (for direct file name requests)
        direct_path = f'logos/{decoded_sportsbook}'
        if os.path.exists(direct_path):
            # Determine MIME type based on file extension
            if decoded_sportsbook.lower().endswith('.png'):
                return send_from_directory('logos', decoded_sportsbook, mimetype='image/png')
            elif decoded_sportsbook.lower().endswith('.jpg') or decoded_sportsbook.lower().endswith('.jpeg'):
                return send_from_directory('logos', decoded_sportsbook, mimetype='image/jpeg')
            else:
                return send_from_directory('logos', decoded_sportsbook)
        
        # Also try the original encoded version
        original_path = f'logos/{sportsbook}'
        if os.path.exists(original_path):
            if sportsbook.lower().endswith('.png'):
                return send_from_directory('logos', sportsbook, mimetype='image/png')
            elif sportsbook.lower().endswith('.jpg') or sportsbook.lower().endswith('.jpeg'):
                return send_from_directory('logos', sportsbook, mimetype='image/jpeg')
            else:
                return send_from_directory('logos', sportsbook)
        
        # Try different file extensions for the sportsbook name
        extensions = ['.png', '.jpg', '.jpeg', '.svg']
        for ext in extensions:
            logo_path = f'logos/{decoded_sportsbook.lower()}{ext}'
            if os.path.exists(logo_path):
                mimetype = 'image/png' if ext == '.png' else 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/svg+xml'
                return send_from_directory('logos', f'{decoded_sportsbook.lower()}{ext}', mimetype=mimetype)
        
        # Generate SVG fallback
        from flask import Response
        import base64
        
        # Color mapping for sportsbooks
        colors = {
            'espn bet': '#d50000',
            'fanatics': '#0066cc',
            'fanduel': '#1e3a8a',
            'draftkings': '#f59e0b', 
            'betmgm': '#059669',
            'caesars': '#dc2626',
            'caesers': '#dc2626',  # Handle misspelling
            'bet365': '#ffb400',
            'unabated': '#4a90e2',
            'betrivers': '#0891b2',
            'pointsbet': '#7c3aed',
            'wynnbet': '#be123c',
            'bovada': '#ea580c',
            'betonline': '#16a34a',
            'bookmaker': '#0f172a',
            'pinnacle': '#dc2626',
            'circa': '#f59e0b'
        }
        
        color = colors.get(sportsbook.lower(), '#4a90e2')
        initial = sportsbook[0].upper()
        
        svg_content = f'''<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="6" fill="{color}"/>
            <text x="16" y="22" font-family="Arial, sans-serif" font-size="16" font-weight="bold" 
                  fill="white" text-anchor="middle">{initial}</text>
        </svg>'''
        
        return Response(svg_content, mimetype='image/svg+xml')
        
    except Exception as e:
        logger.error(f"Error serving logo for {sportsbook}: {e}")
        # Return a simple fallback SVG
        svg_fallback = f'''<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="6" fill="#4a90e2"/>
            <text x="16" y="22" font-family="Arial, sans-serif" font-size="16" font-weight="bold" 
                  fill="white" text-anchor="middle">?</text>
        </svg>'''
        return Response(svg_fallback, mimetype='image/svg+xml')

@app.route('/feed')
def get_feed():
    """Get the complete MLB odds feed."""
    try:
        feed_data = get_cached_feed()
        
        # Check if pretty printing is requested
        pretty = request.args.get('pretty', '').lower() in ['true', '1', 'yes']
        
        if pretty:
            # Return pretty-printed JSON
            response = app.response_class(
                response=json.dumps(feed_data, indent=2, ensure_ascii=False),
                status=200,
                mimetype='application/json'
            )
        else:
            # Return compact JSON
            response = jsonify(feed_data)
        
        # Add cache headers
        response.headers['Cache-Control'] = f'public, max-age={feed_cache["cache_duration_minutes"] * 60}'
        response.headers['X-Total-Games'] = str(feed_data.get('feed_info', {}).get('total_games', 0))
        
        return response
        
    except Exception as e:
        logger.error(f"Error in /feed endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/status')
def get_status():
    """Get API status and cache information."""
    cache_age_seconds = 0
    if feed_cache['last_updated']:
        cache_age_seconds = (datetime.now() - feed_cache['last_updated']).total_seconds()
    
    return jsonify({
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'cache': {
            'has_data': feed_cache['data'] is not None,
            'last_updated': feed_cache['last_updated'].isoformat() if feed_cache['last_updated'] else None,
            'age_seconds': int(cache_age_seconds),
            'cache_duration_minutes': feed_cache['cache_duration_minutes'],
            'is_expired': cache_age_seconds > feed_cache['cache_duration_minutes'] * 60
        },
        'api': {
            'source': 'Unabated API v2.0',
            'endpoint': 'https://partner-api.unabated.com/v2/markets/gameOdds'
        }
    })

@app.route('/games/count')
def get_games_count():
    """Get just the count of games."""
    try:
        feed_data = get_cached_feed()
        total_games = feed_data.get('feed_info', {}).get('total_games', 0)
        
        return jsonify({
            'total_games': total_games,
            'timestamp': datetime.now().isoformat(),
            'source': 'Unabated API v2.0'
        })
        
    except Exception as e:
        logger.error(f"Error in /games/count endpoint: {e}")
        return jsonify({
            'error': 'Unable to fetch game count',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': ['/feed', '/status', '/games/count'],
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    print("🏈 Starting MLB Odds Feed Web Server...")
    print("📊 Feed URL: http://localhost:5000/feed")
    print("📈 Status URL: http://localhost:5000/status")
    print("🏠 Home page: http://localhost:5000/")
    print()
    
    # Run the Flask development server
    app.run(
        host='0.0.0.0',  # Allow external connections
        port=5000,
        debug=False,     # Set to True for development
        threaded=True    # Handle multiple requests
    )
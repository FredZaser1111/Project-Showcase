"""
Ball Don't Lie API client with rate limiting, caching, and retry logic.
Supports both free tier (5 req/min) and GOAT tier (600 req/min).
"""
import time
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import deque
import config

class RateLimiter:
    """Rate limiter with configurable requests per minute."""
    
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute
        self.request_times = deque()
    
    def wait_if_needed(self):
        """Wait if we've exceeded the rate limit."""
        now = time.time()
        
        # Remove requests older than 1 minute
        while self.request_times and now - self.request_times[0] > 60:
            self.request_times.popleft()
        
        # If we're at the limit, wait
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0]) + 0.1
            if sleep_time > 0:
                time.sleep(sleep_time)
                # Clean up old requests after sleep
                now = time.time()
                while self.request_times and now - self.request_times[0] > 60:
                    self.request_times.popleft()
        
        self.request_times.append(time.time())

class APIClient:
    """Client for Ball Don't Lie API with rate limiting and caching."""
    
    def __init__(self, api_key: str = None, rate_limit: int = None):
        self.api_key = api_key or config.API_KEY
        self.rate_limiter = RateLimiter(rate_limit or config.RATE_LIMIT_PER_MIN)
        self.base_url = config.API_BASE_URL
        self.cache_dir = Path(config.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=24)  # Cache for 24 hours
        
        # Request session for connection pooling
        self.session = requests.Session()
        # Ball Don't Lie API may use API key as query parameter or header
        # Try both methods
        if self.api_key:
            # Some APIs use query parameter
            # self.session.params = {'api_key': self.api_key}
            # Others use header
            self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})
            # Or try: self.session.headers.update({'X-API-Key': self.api_key})
    
    def _get_cache_path(self, endpoint: str, params: Dict = None) -> Path:
        """Generate cache file path for an endpoint."""
        cache_key = f"{endpoint}_{json.dumps(params or {}, sort_keys=True)}"
        # Sanitize filename
        cache_key = cache_key.replace('/', '_').replace('?', '_').replace('&', '_')
        return self.cache_dir / f"{cache_key}.json"
    
    def _load_from_cache(self, cache_path: Path) -> Optional[Dict]:
        """Load data from cache if it exists and is not expired."""
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
            
            # Check if cache is expired
            cache_time = datetime.fromisoformat(cached_data.get('cached_at', ''))
            if datetime.now() - cache_time > self.cache_ttl:
                return None
            
            return cached_data.get('data')
        except Exception:
            return None
    
    def _save_to_cache(self, cache_path: Path, data: Dict):
        """Save data to cache."""
        try:
            cache_data = {
                'cached_at': datetime.now().isoformat(),
                'data': data
            }
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception:
            pass  # Silently fail if cache write fails
    
    def _make_request(self, endpoint: str, params: Dict = None, use_cache: bool = True) -> Dict:
        """
        Make API request with rate limiting, caching, and retry logic.
        
        Args:
            endpoint: API endpoint (e.g., 'teams', 'games')
            params: Query parameters
            use_cache: Whether to use cache
        
        Returns:
            API response data
        """
        params = params or {}
        cache_path = self._get_cache_path(endpoint, params)
        
        # Try cache first
        if use_cache:
            cached_data = self._load_from_cache(cache_path)
            if cached_data is not None:
                return cached_data
        
        # Rate limit
        self.rate_limiter.wait_if_needed()
        
        # Make request with retry logic
        url = f"{self.base_url}/{endpoint}"
        max_retries = 3
        retry_delay = 1
        
        # Add API key to params if provided (some APIs use this method)
        request_params = params.copy() if params else {}
        if self.api_key and 'api_key' not in request_params:
            # Try as query parameter (some APIs prefer this)
            request_params['api_key'] = self.api_key
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=request_params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                # Save to cache
                if use_cache:
                    self._save_to_cache(cache_path, data)
                
                return data
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise Exception(f"API request failed after {max_retries} attempts: {str(e)}")
    
    def get_teams(self, page: int = 0, per_page: int = 30) -> Dict:
        """Get list of NBA teams."""
        params = {'page': page, 'per_page': per_page}
        return self._make_request('teams', params)
    
    def get_all_teams(self) -> List[Dict]:
        """Get all NBA teams (handles pagination)."""
        all_teams = []
        page = 0
        per_page = 100
        
        while True:
            response = self.get_teams(page=page, per_page=per_page)
            teams = response.get('data', [])
            if not teams:
                break
            all_teams.extend(teams)
            
            # Check if there are more pages
            meta = response.get('meta', {})
            if page >= meta.get('total_pages', 1) - 1:
                break
            page += 1
        
        return all_teams
    
    def get_games(self, dates: List[str] = None, team_ids: List[int] = None, 
                  seasons: List[int] = None, page: int = 0, per_page: int = 100) -> Dict:
        """
        Get games with optional filters.
        
        Args:
            dates: List of dates in YYYY-MM-DD format
            team_ids: List of team IDs to filter by
            seasons: List of seasons (e.g., [2023] for 2023-24 season)
            page: Page number
            per_page: Items per page
        """
        params = {'page': page, 'per_page': per_page}
        
        if dates:
            params['dates[]'] = dates
        if team_ids:
            params['team_ids[]'] = team_ids
        if seasons:
            params['seasons[]'] = seasons
        
        return self._make_request('games', params)
    
    def get_all_games(self, dates: List[str] = None, team_ids: List[int] = None,
                      seasons: List[int] = None) -> List[Dict]:
        """Get all games matching filters (handles pagination)."""
        all_games = []
        page = 0
        per_page = 100
        
        while True:
            response = self.get_games(dates=dates, team_ids=team_ids, 
                                    seasons=seasons, page=page, per_page=per_page)
            games = response.get('data', [])
            if not games:
                break
            all_games.extend(games)
            
            # Check if there are more pages
            meta = response.get('meta', {})
            if page >= meta.get('total_pages', 1) - 1:
                break
            page += 1
        
        return all_games
    
    def get_team_stats(self, team_id: int, season: int = None) -> Dict:
        """Get team statistics."""
        params = {'team_ids[]': [team_id]}
        if season:
            params['seasons[]'] = [season]
        
        # Note: Ball Don't Lie API may have different endpoints for stats
        # This is a placeholder - adjust based on actual API structure
        return self._make_request('games', params)
    
    def get_player_stats(self, player_id: int = None, team_id: int = None,
                        season: int = None, page: int = 0, per_page: int = 100) -> Dict:
        """Get player statistics."""
        params = {'page': page, 'per_page': per_page}
        
        if player_id:
            params['player_ids[]'] = [player_id]
        if team_id:
            params['team_ids[]'] = [team_id]
        if season:
            params['seasons[]'] = [season]
        
        return self._make_request('stats', params)
    
    def get_game_by_id(self, game_id: int) -> Dict:
        """Get specific game by ID."""
        return self._make_request(f'games/{game_id}')


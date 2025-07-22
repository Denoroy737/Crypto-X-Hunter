"""
Twitter Scraper Module for XScanner
Fetches tweets using snscrape (no API key needed) or X API v2
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys


class TwitterScraper:
    def __init__(self, config):
        self.config = config
        self.twitter_config = config.get('twitter', {})
        self.hashtags = self.twitter_config.get('hashtags', [])
        self.max_tweets = self.twitter_config.get('max_tweets', 100)
        self.days_back = self.twitter_config.get('days_back', 1)
        
        # Load influencer accounts if available
        self.influencer_accounts = self._load_influencers()
    
    def _load_influencers(self):
        """Load influencer accounts from file"""
        try:
            with open('data/influencers.txt', 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            return []
    
    async def fetch_tweets(self):
        """Main method to fetch tweets"""
        try:
            # Try snscrape first (no API key needed)
            return await self._fetch_with_snscrape()
        except Exception as e:
            print(f"⚠️ snscrape failed: {e}")
            # Fallback to X API if available
            return await self._fetch_with_xapi()
    
    async def _fetch_with_snscrape(self):
        """Fetch tweets using snscrape"""
        tweets = []
        since_date = (datetime.now() - timedelta(days=self.days_back)).strftime('%Y-%m-%d')
        
        # Search by hashtags
        for hashtag in self.hashtags:
            query = f"{hashtag} since:{since_date}"
            tweets.extend(await self._run_snscrape_search(query, self.max_tweets // len(self.hashtags)))
        
        # Search influencer accounts
        for account in self.influencer_accounts[:5]:  # Limit to avoid rate limits
            query = f"from:{account} since:{since_date}"
            tweets.extend(await self._run_snscrape_search(query, 20))
        
        return self._deduplicate_tweets(tweets)
    
    async def _run_snscrape_search(self, query, limit):
        """Run snscrape command and parse results"""
        try:
            cmd = [
                sys.executable, '-m', 'snscrape', '--jsonl', '--max-results', str(limit),
                'twitter-search', query
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                print(f"snscrape error: {stderr.decode()}")
                return []
            
            tweets = []
            for line in stdout.decode().strip().split('\n'):
                if line:
                    try:
                        tweet_data = json.loads(line)
                        tweets.append(self._format_tweet(tweet_data))
                    except json.JSONDecodeError:
                        continue
            
            return tweets
            
        except Exception as e:
            print(f"Error running snscrape: {e}")
            return []
    
    async def _fetch_with_xapi(self):
        """Fetch tweets using X API v2 (if API key is provided)"""
        api_key = self.twitter_config.get('api_key')
        if not api_key:
            print("⚠️ No X API key provided, using mock data")
            return self._get_mock_tweets()
        
        # TODO: Implement X API v2 integration
        print("🔧 X API v2 integration not implemented yet, using mock data")
        return self._get_mock_tweets()
    
    def _format_tweet(self, raw_tweet):
        """Format tweet data into standardized structure"""
        return {
            'id': raw_tweet.get('id'),
            'text': raw_tweet.get('rawContent', raw_tweet.get('content', '')),
            'author': raw_tweet.get('user', {}).get('username'),
            'author_followers': raw_tweet.get('user', {}).get('followersCount', 0),
            'created_at': raw_tweet.get('date'),
            'retweets': raw_tweet.get('retweetCount', 0),
            'likes': raw_tweet.get('likeCount', 0),
            'url': raw_tweet.get('url', ''),
            'raw_data': raw_tweet
        }
    
    def _deduplicate_tweets(self, tweets):
        """Remove duplicate tweets based on ID"""
        seen = set()
        unique_tweets = []
        
        for tweet in tweets:
            if tweet['id'] not in seen:
                seen.add(tweet['id'])
                unique_tweets.append(tweet)
        
        return unique_tweets[:self.max_tweets]
    
    def _get_mock_tweets(self):
        """Mock tweets for testing when APIs are unavailable"""
        return [
            {
                'id': '1',
                'text': '🚀 Exciting news! LayerZero is launching a massive #airdrop campaign. Early supporters get 2x rewards! Connect your wallet at layerzero.network #crypto #DeFi',
                'author': 'cryptowhale',
                'author_followers': 50000,
                'created_at': datetime.now().isoformat(),
                'retweets': 245,
                'likes': 892,
                'url': 'https://twitter.com/cryptowhale/status/1'
            },
            {
                'id': '2',
                'text': '📢 BREAKING: Polygon Labs just closed a $15M Series A round led by Sequoia Capital! Building the future of Web3 infrastructure on Ethereum. 🔥 #funding #polygon #ethereum',
                'author': 'web3insider',
                'author_followers': 25000,
                'created_at': datetime.now().isoformat(),
                'retweets': 156,
                'likes': 423,
                'url': 'https://twitter.com/web3insider/status/2'
            },
            {
                'id': '3',
                'text': '🎯 New project alert! ZkSync Era is giving away tokens to early testnet users. Claim yours before the snapshot! #airdrop #zksync #layer2',
                'author': 'airdrophunter',
                'author_followers': 15000,
                'created_at': datetime.now().isoformat(),
                'retweets': 89,
                'likes': 234,
                'url': 'https://twitter.com/airdrophunter/status/3'
            },
            {
                'id': '4',
                'text': '💡 Introducing ChainLink 3.0 - revolutionizing oracle networks with AI-powered data feeds. Pre-seed round opening soon. Interested VCs, DM us! #startup #oracle #AI',
                'author': 'chainlink_team',
                'author_followers': 100000,
                'created_at': datetime.now().isoformat(),
                'retweets': 445,
                'likes': 1200,
                'url': 'https://twitter.com/chainlink_team/status/4'
            },
            {
                'id': '5',
                'text': 'Just had my coffee ☕ and thinking about the weekend plans. Maybe visit the beach 🏖️ #life #weekend',
                'author': 'randomuser',
                'author_followers': 100,
                'created_at': datetime.now().isoformat(),
                'retweets': 2,
                'likes': 5,
                'url': 'https://twitter.com/randomuser/status/5'
            }
        ]


# Installation helper
def install_snscrape():
    """Install snscrape if not available"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'snscrape'])
        print("✅ snscrape installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install snscrape")
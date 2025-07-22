"""
Grok AI Classifier Module for XScanner
Uses Grok API for semantic analysis and structured data extraction
"""

import json
import asyncio
import aiohttp
from datetime import datetime


class GrokClassifier:
    def __init__(self, config):
        self.config = config
        self.grok_config = config.get('grok', {})
        self.api_key = self.grok_config.get('api_key')
        self.model = self.grok_config.get('model', 'grok-beta')
        self.base_url = 'https://api.x.ai/v1'
        
        # Classification prompt template
        self.system_prompt = """You are an expert crypto analyst specializing in identifying airdrops and early-stage crypto startups from social media posts.

Analyze the given tweet and classify it into one of three categories:
1. "airdrop" - Posts about token airdrops, free token distributions, or reward campaigns
2. "startup" - Posts about new crypto projects, funding rounds, or early-stage ventures
3. "ignore" - Posts that don't fit the above categories (personal updates, news, etc.)

For "airdrop" and "startup" classifications, extract structured information.

Return your response as a valid JSON object with this exact structure:
{
    "type": "airdrop|startup|ignore",
    "confidence": 0.0-1.0,
    "project_name": "string or null",
    "chain": "string or null",
    "category": "string or null", 
    "funding_amount": "string or null",
    "investors": ["list of strings or empty"],
    "website": "string or null",
    "description": "brief description or null",
    "key_features": ["list of strings or empty"],
    "reasoning": "brief explanation of classification"
}

Categories for startups: DeFi, L2, AI, Gaming, Infrastructure, NFT, DAO, etc.
Chains: Ethereum, Polygon, Solana, Arbitrum, Base, etc."""
    
    async def classify_tweet(self, tweet):
        """Classify a single tweet using Grok API"""
        if not self.api_key or self.api_key == 'your_grok_api_key_here':
            # Use mock classification for testing
            return self._mock_classify(tweet)
        
        try:
            result = await self._call_grok_api(tweet)
            if result:
                # Add metadata from original tweet
                result.update({
                    'tweet_id': tweet['id'],
                    'tweet_url': tweet['url'],
                    'author': tweet['author'],
                    'author_followers': tweet['author_followers'],
                    'engagement': tweet['likes'] + tweet['retweets'],
                    'created_at': tweet['created_at'],
                    'original_text': tweet['text']
                })
            return result
        except Exception as e:
            print(f"Error classifying tweet {tweet['id']}: {e}")
            return None
    
    async def _call_grok_api(self, tweet):
        """Make API call to Grok"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messages': [
                {
                    'role': 'system',
                    'content': self.system_prompt
                },
                {
                    'role': 'user',
                    'content': f'Tweet text: "{tweet["text"]}"\n\nAuthor: @{tweet["author"]} ({tweet["author_followers"]} followers)\nEngagement: {tweet["likes"]} likes, {tweet["retweets"]} retweets'
                }
            ],
            'model': self.model,
            'temperature': 0.1,
            'max_tokens': 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data['choices'][0]['message']['content']
                    return self._parse_grok_response(content)
                else:
                    error_text = await response.text()
                    print(f"Grok API error {response.status}: {error_text}")
                    return None
    
    def _parse_grok_response(self, content):
        """Parse Grok API response and extract JSON"""
        try:
            # Try to find JSON in the response
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                print(f"No valid JSON found in Grok response: {content}")
                return None
        except json.JSONDecodeError as e:
            print(f"Failed to parse Grok JSON response: {e}")
            print(f"Content: {content}")
            return None
    
    def _mock_classify(self, tweet):
        """Mock classification for testing without API key"""
        text = tweet['text'].lower()
        
        # Simple keyword-based classification for testing
        airdrop_keywords = ['airdrop', 'free tokens', 'claim', 'reward', 'distribution', 'snapshot']
        startup_keywords = ['funding', 'series a', 'seed', 'pre-seed', 'raised', 'led by', 'investors', 'launch', 'announcing']
        
        # Check for airdrops
        if any(keyword in text for keyword in airdrop_keywords):
            return {
                'type': 'airdrop',
                'confidence': 0.8,
                'project_name': self._extract_project_name(tweet['text']),
                'chain': self._extract_chain(tweet['text']),
                'category': 'Token Distribution',
                'funding_amount': None,
                'investors': [],
                'website': self._extract_website(tweet['text']),
                'description': 'Potential airdrop opportunity detected',
                'key_features': ['Free tokens', 'Community rewards'],
                'reasoning': 'Contains airdrop-related keywords',
                'tweet_id': tweet['id'],
                'tweet_url': tweet['url'],
                'author': tweet['author'],
                'author_followers': tweet['author_followers'],
                'engagement': tweet['likes'] + tweet['retweets'],
                'created_at': tweet['created_at'],
                'original_text': tweet['text']
            }
        
        # Check for startups
        elif any(keyword in text for keyword in startup_keywords):
            return {
                'type': 'startup',
                'confidence': 0.8,
                'project_name': self._extract_project_name(tweet['text']),
                'chain': self._extract_chain(tweet['text']),
                'category': self._extract_category(tweet['text']),
                'funding_amount': self._extract_funding(tweet['text']),
                'investors': self._extract_investors(tweet['text']),
                'website': self._extract_website(tweet['text']),
                'description': 'Early-stage crypto startup detected',
                'key_features': ['Funding announcement', 'New project launch'],
                'reasoning': 'Contains startup/funding-related keywords',
                'tweet_id': tweet['id'],
                'tweet_url': tweet['url'],
                'author': tweet['author'],
                'author_followers': tweet['author_followers'],
                'engagement': tweet['likes'] + tweet['retweets'],
                'created_at': tweet['created_at'],
                'original_text': tweet['text']
            }
        
        else:
            return {
                'type': 'ignore',
                'confidence': 0.9,
                'project_name': None,
                'chain': None,
                'category': None,
                'funding_amount': None,
                'investors': [],
                'website': None,
                'description': None,
                'key_features': [],
                'reasoning': 'No crypto/startup/airdrop relevance detected',
                'tweet_id': tweet['id'],
                'tweet_url': tweet['url'],
                'author': tweet['author'],
                'author_followers': tweet['author_followers'],
                'engagement': tweet['likes'] + tweet['retweets'],
                'created_at': tweet['created_at'],
                'original_text': tweet['text']
            }
    
    def _extract_project_name(self, text):
        """Extract potential project name"""
        # Simple extraction - look for capitalized words
        words = text.split()
        for word in words:
            if word[0].isupper() and len(word) > 3 and word.isalpha():
                return word
        return None
    
    def _extract_chain(self, text):
        """Extract blockchain/chain mentions"""
        chains = ['ethereum', 'polygon', 'solana', 'arbitrum', 'base', 'optimism', 'avalanche']
        text_lower = text.lower()
        for chain in chains:
            if chain in text_lower:
                return chain.capitalize()
        return None
    
    def _extract_category(self, text):
        """Extract project category"""
        categories = ['defi', 'nft', 'gaming', 'dao', 'infrastructure', 'ai', 'layer2', 'l2']
        text_lower = text.lower()
        for cat in categories:
            if cat in text_lower:
                return cat.upper() if cat in ['ai', 'l2'] else cat.capitalize()
        return 'Infrastructure'
    
    def _extract_funding(self, text):
        """Extract funding amount"""
        import re
        funding_pattern = r'\$(\d+(?:\.\d+)?)\s*([mM]|[bB]|million|billion)'
        match = re.search(funding_pattern, text)
        if match:
            return f"${match.group(1)}{match.group(2).upper() if match.group(2).lower() in ['m', 'b'] else match.group(2).lower()}"
        return None
    
    def _extract_investors(self, text):
        """Extract investor mentions"""
        # Common VC names
        vcs = ['sequoia', 'a16z', 'binance labs', 'coinbase ventures', 'paradigm']
        investors = []
        text_lower = text.lower()
        for vc in vcs:
            if vc in text_lower:
                investors.append(vc.title())
        return investors
    
    def _extract_website(self, text):
        """Extract website URLs"""
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return urls[0] if urls else None


# Batch processing utilities
async def classify_batch(classifier, tweets, batch_size=10):
    """Classify tweets in batches to avoid rate limiting"""
    results = []
    for i in range(0, len(tweets), batch_size):
        batch = tweets[i:i + batch_size]
        tasks = [classifier.classify_tweet(tweet) for tweet in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in batch_results:
            if not isinstance(result, Exception) and result:
                results.append(result)
        
        # Small delay between batches
        await asyncio.sleep(1)
    
    return results
#!/usr/bin/env python3
"""
XScanner - AI-powered crypto airdrop and startup discovery tool
Main orchestrator script
"""

import asyncio
import yaml
from datetime import datetime
from pathlib import Path

from modules.twitter_scraper import TwitterScraper
from modules.grok_classifier import GrokClassifier
from modules.storage import DataStorage


class XScanner:
    def __init__(self, config_path="config/settings.yaml"):
        self.config = self._load_config(config_path)
        self.twitter_scraper = TwitterScraper(self.config)
        self.grok_classifier = GrokClassifier(self.config)
        self.storage = DataStorage(self.config)
        
    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Config file not found: {config_path}")
            return self._default_config()
    
    def _default_config(self):
        """Default configuration if file not found"""
        return {
            'twitter': {
                'hashtags': ['#airdrop', '#launch', '#raising', '#seed', '#preseed', '#funding'],
                'max_tweets': 100,
                'days_back': 1
            },
            'grok': {
                'api_key': 'your_grok_api_key_here',
                'model': 'grok-beta'
            },
            'storage': {
                'csv_path': 'data/results',
                'batch_size': 50
            }
        }
    
    async def scan_and_classify(self):
        """Main scanning and classification process"""
        print("🚀 Starting XScanner...")
        
        # Step 1: Scrape tweets
        print("📡 Fetching tweets...")
        tweets = await self.twitter_scraper.fetch_tweets()
        print(f"✅ Found {len(tweets)} tweets")
        
        if not tweets:
            print("❌ No tweets found. Exiting...")
            return
        
        # Step 2: Classify with Grok
        print("🤖 Classifying tweets with Grok AI...")
        classified_data = []
        
        batch_size = self.config.get('storage', {}).get('batch_size', 50)
        for i in range(0, len(tweets), batch_size):
            batch = tweets[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(tweets) + batch_size - 1)//batch_size}")
            
            for tweet in batch:
                try:
                    result = await self.grok_classifier.classify_tweet(tweet)
                    if result and result.get('type') != 'ignore':
                        classified_data.append(result)
                        print(f"✅ {result['type']}: {result.get('project_name', 'Unknown')}")
                except Exception as e:
                    print(f"❌ Error processing tweet: {e}")
                    continue
        
        # Step 3: Store results
        print(f"💾 Saving {len(classified_data)} classified items...")
        self.storage.save_results(classified_data)
        
        # Summary
        airdrops = sum(1 for item in classified_data if item['type'] == 'airdrop')
        startups = sum(1 for item in classified_data if item['type'] == 'startup')
        
        print("\n🎯 Scan Complete!")
        print(f"📊 Results: {airdrops} airdrops, {startups} startups")
        print(f"📁 Data saved to: {self.storage.get_output_path()}")
        
        return classified_data
    
    async def run_continuous_scan(self, interval_hours=6):
        """Run scanner continuously"""
        print(f"🔄 Starting continuous scan (every {interval_hours} hours)")
        while True:
            await self.scan_and_classify()
            print(f"😴 Sleeping for {interval_hours} hours...")
            await asyncio.sleep(interval_hours * 3600)


async def main():
    """Main entry point"""
    scanner = XScanner()
    
    # Run once or continuously
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        await scanner.run_continuous_scan()
    else:
        await scanner.scan_and_classify()


if __name__ == "__main__":
    asyncio.run(main())
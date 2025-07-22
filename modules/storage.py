"""
Data Storage Module for XScanner
Handles CSV export and future MongoDB/Notion integration
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd


class DataStorage:
    def __init__(self, config):
        self.config = config
        self.storage_config = config.get('storage', {})
        self.csv_path = self.storage_config.get('csv_path', 'data/results')
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories"""
        Path(self.csv_path).mkdir(parents=True, exist_ok=True)
        Path('data').mkdir(exist_ok=True)
    
    def save_results(self, classified_data):
        """Save classified results to CSV files"""
        if not classified_data:
            print("⚠️ No data to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Separate airdrops and startups
        airdrops = [item for item in classified_data if item['type'] == 'airdrop']
        startups = [item for item in classified_data if item['type'] == 'startup']
        
        # Save airdrops
        if airdrops:
            airdrop_file = f"{self.csv_path}/airdrops_{timestamp}.csv"
            self._save_to_csv(airdrops, airdrop_file, 'airdrop')
            print(f"💰 Saved {len(airdrops)} airdrops to {airdrop_file}")
        
        # Save startups
        if startups:
            startup_file = f"{self.csv_path}/startups_{timestamp}.csv"
            self._save_to_csv(startups, startup_file, 'startup')
            print(f"🚀 Saved {len(startups)} startups to {startup_file}")
        
        # Save combined results
        combined_file = f"{self.csv_path}/combined_{timestamp}.csv"
        self._save_to_csv(classified_data, combined_file, 'combined')
        print(f"📊 Saved {len(classified_data)} total results to {combined_file}")
        
        # Save summary statistics
        self._save_summary(classified_data, timestamp)
        
        return {
            'airdrops': len(airdrops),
            'startups': len(startups),
            'total': len(classified_data),
            'files': {
                'airdrops': airdrop_file if airdrops else None,
                'startups': startup_file if startups else None,
                'combined': combined_file
            }
        }
    
    def _save_to_csv(self, data, filename, data_type):
        """Save data to CSV with appropriate columns"""
        if not data:
            return
        
        # Define columns based on type
        if data_type == 'airdrop':
            columns = [
                'project_name', 'chain', 'category', 'confidence', 'website',
                'description', 'key_features', 'author', 'author_followers',
                'engagement', 'tweet_url', 'created_at', 'original_text', 'reasoning'
            ]
        elif data_type == 'startup':
            columns = [
                'project_name', 'chain', 'category', 'funding_amount', 'investors',
                'confidence', 'website', 'description', 'key_features', 
                'author', 'author_followers', 'engagement', 'tweet_url', 
                'created_at', 'original_text', 'reasoning'
            ]
        else:  # combined
            columns = [
                'type', 'project_name', 'chain', 'category', 'funding_amount',
                'investors', 'confidence', 'website', 'description', 'key_features',
                'author', 'author_followers', 'engagement', 'tweet_url',
                'created_at', 'original_text', 'reasoning'
            ]
        
        # Prepare data for CSV
        csv_data = []
        for item in data:
            row = {}
            for col in columns:
                value = item.get(col)
                
                # Handle list fields
                if isinstance(value, list):
                    row[col] = '; '.join(value) if value else ''
                # Handle None values
                elif value is None:
                    row[col] = ''
                else:
                    row[col] = str(value)
            
            csv_data.append(row)
        
        # Write to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            writer.writerows(csv_data)
    
    def _save_summary(self, data, timestamp):
        """Save summary statistics"""
        summary = {
            'scan_timestamp': timestamp,
            'total_items': len(data),
            'airdrops': len([item for item in data if item['type'] == 'airdrop']),
            'startups': len([item for item in data if item['type'] == 'startup']),
            'top_chains': self._get_top_chains(data),
            'top_categories': self._get_top_categories(data),
            'high_engagement': len([item for item in data if item.get('engagement', 0) > 100]),
            'verified_authors': len([item for item in data if item.get('author_followers', 0) > 10000])
        }
        
        summary_file = f"{self.csv_path}/summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def _get_top_chains(self, data):
        """Get most mentioned chains"""
        chains = {}
        for item in data:
            chain = item.get('chain')
            if chain:
                chains[chain] = chains.get(chain, 0) + 1
        return sorted(chains.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _get_top_categories(self, data):
        """Get most common categories"""
        categories = {}
        for item in data:
            category = item.get('category')
            if category:
                categories[category] = categories.get(category, 0) + 1
        return sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def get_output_path(self):
        """Return the output directory path"""
        return os.path.abspath(self.csv_path)
    
    def load_historical_data(self, days_back=7):
        """Load historical data from CSV files"""
        try:
            historical_data = []
            csv_files = Path(self.csv_path).glob("combined_*.csv")
            
            for file_path in sorted(csv_files)[-days_back:]:  # Last N files
                df = pd.read_csv(file_path)
                historical_data.extend(df.to_dict('records'))
            
            return historical_data
        except Exception as e:
            print(f"Error loading historical data: {e}")
            return []
    
    def export_to_notion(self, data):
        """Export data to Notion (future implementation)"""
        # TODO: Implement Notion API integration
        print("🔧 Notion export not implemented yet")
        pass
    
    def export_to_mongodb(self, data):
        """Export data to MongoDB (future implementation)"""
        # TODO: Implement MongoDB integration
        print("🔧 MongoDB export not implemented yet")
        pass
    
    def export_to_telegram(self, data):
        """Send summary to Telegram (future implementation)"""
        # TODO: Implement Telegram bot integration
        print("🔧 Telegram export not implemented yet")
        pass
    
    def get_analytics(self, data):
        """Generate analytics from the data"""
        if not data:
            return {}
        
        analytics = {
            'total_opportunities': len(data),
            'airdrops_vs_startups': {
                'airdrops': len([item for item in data if item['type'] == 'airdrop']),
                'startups': len([item for item in data if item['type'] == 'startup'])
            },
            'confidence_distribution': {
                'high': len([item for item in data if item.get('confidence', 0) > 0.8]),
                'medium': len([item for item in data if 0.6 < item.get('confidence', 0) <= 0.8]),
                'low': len([item for item in data if item.get('confidence', 0) <= 0.6])
            },
            'engagement_stats': {
                'high_engagement': len([item for item in data if item.get('engagement', 0) > 500]),
                'medium_engagement': len([item for item in data if 100 < item.get('engagement', 0) <= 500]),
                'low_engagement': len([item for item in data if item.get('engagement', 0) <= 100])
            },
            'top_chains': self._get_top_chains(data),
            'top_categories': self._get_top_categories(data),
            'funding_insights': self._analyze_funding(data)
        }
        
        return analytics
    
    def _analyze_funding(self, data):
        """Analyze funding-related data"""
        funded_projects = [item for item in data if item.get('funding_amount')]
        
        if not funded_projects:
            return {'total_funded': 0}
        
        return {
            'total_funded': len(funded_projects),
            'avg_confidence': sum(item.get('confidence', 0) for item in funded_projects) / len(funded_projects),
            'top_investors': self._get_top_investors(funded_projects)
        }
    
    def _get_top_investors(self, data):
        """Get most active investors"""
        investors = {}
        for item in data:
            investor_list = item.get('investors', [])
            if isinstance(investor_list, str):
                investor_list = investor_list.split(';')
            
            for investor in investor_list:
                investor = investor.strip()
                if investor:
                    investors[investor] = investors.get(investor, 0) + 1
        
        return sorted(investors.items(), key=lambda x: x[1], reverse=True)[:5]


# Utility functions for data management
class DataManager:
    """Additional utilities for managing XScanner data"""
    
    def __init__(self, storage_path='data/results'):
        self.storage_path = storage_path
    
    def merge_csv_files(self, pattern="combined_*.csv", output_file=None):
        """Merge multiple CSV files into one"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.storage_path}/merged_{timestamp}.csv"
        
        csv_files = list(Path(self.storage_path).glob(pattern))
        if not csv_files:
            print("No CSV files found to merge")
            return
        
        combined_df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
        combined_df.drop_duplicates(subset=['tweet_url'], keep='first', inplace=True)
        combined_df.to_csv(output_file, index=False)
        
        print(f"📊 Merged {len(csv_files)} files into {output_file}")
        print(f"📈 Total unique records: {len(combined_df)}")
        
        return output_file
    
    def clean_old_files(self, days_to_keep=30):
        """Remove old CSV files"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        removed_count = 0
        
        for file_path in Path(self.storage_path).glob("*.csv"):
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_time < cutoff_date:
                file_path.unlink()
                removed_count += 1
        
        print(f"🧹 Cleaned {removed_count} old files")
    
    def generate_report(self, days_back=7):
        """Generate a summary report"""
        storage = DataStorage({'storage': {'csv_path': self.storage_path}})
        historical_data = storage.load_historical_data(days_back)
        
        if not historical_data:
            print("No historical data found")
            return
        
        analytics = storage.get_analytics(historical_data)
        
        # Generate markdown report
        report = f"""# XScanner Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Data Period: Last {days_back} scans

## Summary
- **Total Opportunities**: {analytics['total_opportunities']}
- **Airdrops**: {analytics['airdrops_vs_startups']['airdrops']}
- **Startups**: {analytics['airdrops_vs_startups']['startups']}

## Top Chains
{chr(10).join([f"- {chain}: {count}" for chain, count in analytics['top_chains']])}

## Top Categories  
{chr(10).join([f"- {cat}: {count}" for cat, count in analytics['top_categories']])}

## Engagement Distribution
- High (>500): {analytics['engagement_stats']['high_engagement']}
- Medium (100-500): {analytics['engagement_stats']['medium_engagement']}
- Low (<100): {analytics['engagement_stats']['low_engagement']}
"""
        
        report_file = f"{self.storage_path}/report_{datetime.now().strftime('%Y%m%d')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📝 Report generated: {report_file}")
        return report_file
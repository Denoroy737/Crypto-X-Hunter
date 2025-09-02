# 🎯 Crypto-X-Hunter - AI-Powered Crypto Opportunity Discovery

**Discover airdrops and early crypto startups before they go viral** using advanced AI semantic analysis powered by Grok API.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Configuration
```bash
# Create config directory
mkdir -p config data/results logs

# Copy and edit configuration
cp config/settings.yaml.example config/settings.yaml
# Edit settings.yaml with your API keys
```

### 3. Add Your API Keys
Edit `config/settings.yaml`:
```yaml
grok:
  api_key: "your_grok_api_key_here"  # Get from https://console.x.ai

twitter:  # Optional - uses snscrape if not provided
  api_key: "your_x_api_key"
  bearer_token: "your_bearer_token"
```

### 4. Run Your First Scan
```bash
python main.py
```

### 5. View Results
```bash
# Results saved to data/results/
ls data/results/

# View latest opportunities
python -c "
import pandas as pd
df = pd.read_csv('data/results/combined_*.csv')
print(df[df['type'] == 'airdrop'][['project_name', 'confidence', 'chain']].head())
"
```

## 📊 Features

### 🤖 AI-Powered Classification
- **Grok API Integration**: Deep semantic understanding beyond keywords
- **Structured Extraction**: Project name, funding, investors, chains
- **Confidence Scoring**: Filter high-quality opportunities

### 🐦 Smart Twitter Monitoring
- **Hashtag Tracking**: `#airdrop`, `#funding`, `#launch`, etc.
- **Influencer Monitoring**: VCs, founders, alpha callers
- **No API Limits**: Uses `snscrape` when Twitter API unavailable

### 💾 Organized Data Export
- **Separate Files**: Airdrops and startups in different CSVs
- **Rich Metadata**: Engagement, confidence, author info
- **Analytics**: Summary reports and trend analysis

## 🧩 Usage Examples

### Single Scan
```bash
python main.py
```

### Continuous Monitoring
```bash
python main.py --continuous
```

### Custom Configuration
```python
from main import XScanner

# Initialize with custom config
scanner = XScanner("path/to/custom/config.yaml")

# Run scan
results = await scanner.scan_and_classify()

# Get analytics
from modules.storage import DataStorage
storage = DataStorage(scanner.config)
analytics = storage.get_analytics(results)
print(f"Found {analytics['airdrops_vs_startups']['airdrops']} airdrops")
```

## 📁 Project Structure

```
xscanner/
├── main.py                 # Main orchestrator
├── config/
│   └── settings.yaml       # Configuration file
├── modules/
│   ├── twitter_scraper.py  # Tweet collection
│   ├── grok_classifier.py  # AI classification
│   └── storage.py          # Data export
├── data/
│   ├── influencers.txt     # VCs and influencers to monitor
│   └── results/            # Output CSV files
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## ⚙️ Configuration Options

### Twitter Monitoring
```yaml
twitter:
  hashtags:
    - "#airdrop"
    - "#funding" 
    - "#launch"
  max_tweets: 200
  days_back: 1
```

### AI Classification
```yaml
grok:
  api_key: "your_key"
  confidence_threshold: 0.6
  batch_size: 10
```

### Data Storage
```yaml
storage:
  csv_path: "data/results"
  keep_files_days: 30
  export_formats: ["csv", "json"]
```

## 📈 Sample Output

### Airdrops CSV
| project_name | chain | confidence | website | description | engagement |
|--------------|-------|------------|---------|-------------|------------|
| LayerZero | Ethereum | 0.85 | layerzero.network | Token distribution campaign | 892 |
| ZkSync Era | Ethereum | 0.78 | zksync.io | Testnet rewards program | 234 |

### Startups CSV  
| project_name | funding_amount | investors | category | confidence | chain |
|--------------|----------------|-----------|----------|------------|-------|
| Polygon Labs | $15M | Sequoia Capital | Infrastructure | 0.92 | Ethereum |
| ChainLink 3.0 | Pre-seed | - | Oracle | 0.81 | Multi-chain |

## 🔧 Advanced Usage

### Custom Filters
```python
# Filter high-confidence opportunities
high_conf = [item for item in results if item['confidence'] > 0.8]

# Filter by funding amount
funded = [item for item in results if item.get('funding_amount')]

# Filter by engagement
viral = [item for item in results if item['engagement'] > 500]
```

### Data Analytics
```python
from modules.storage import DataManager

dm = DataManager()

# Generate weekly report
dm.generate_report(days_back=7)

# Merge historical data
dm.merge_csv_files("airdrops_*.csv", "all_airdrops.csv")

# Clean old files
dm.clean_old_files(days_to_keep=30)
```

## 🚨 Important Notes

### API Requirements
- **Grok API**: Required for AI classification. Get key from [https://console.x.ai](https://console.x.ai)
- **Twitter API**: Optional. Uses free `snscrape` if not provided

### Rate Limits
- **Grok API**: ~50 requests/minute (check your plan)
- **Twitter/snscrape**: No official limits, but use responsibly
- **Built-in Delays**: Automatic rate limiting to avoid blocks

### Data Privacy
- Only processes public tweets
- No personal data storage
- Respects Twitter's terms of service

## 🔮 Future Roadmap

### Phase 2: Enhanced Integrations
- [ ] **MongoDB** storage for better querying
- [ ] **Notion** database sync for organized tracking
- [ ] **Telegram** alerts for high-value opportunities
- [ ] **Google Sheets** export for team collaboration

### Phase 3: Advanced Features
- [ ] **Sentiment Analysis** for market timing
- [ ] **Network Analysis** to find connected projects
- [ ] **Price Prediction** for airdrop values
- [ ] **Portfolio Tracking** for claimed airdrops

### Phase 4: Scale & Automation  
- [ ] **Web Dashboard** for real-time monitoring
- [ ] **Mobile App** for on-the-go alerts
- [ ] **API Endpoints** for third-party integrations
- [ ] **Machine Learning** for improved classification

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Commit** changes: `git commit -am 'Add feature'`
4. **Push** to branch: `git push origin feature-name`
5. **Submit** a Pull Request

## 📜 License

MIT License - feel free to use for personal or commercial projects.

## ⚠️ Disclaimer

This tool is for informational purposes only. Always do your own research (DYOR) before participating in any airdrops or investing in crypto projects. The authors are not responsible for any financial losses.

---

**Happy Hunting! 🎯**

*Find the next big airdrop before it trends*



```markdown
# AEO Watcher

AEO Watcher is a powerful analytics tool that helps analyze and track brand recommendations made by Large Language Models (LLMs). It provides real-time insights into which brands AI models are suggesting across different categories and queries.

## Features

- **Multi-Model Analysis**: Test brand recommendations across different LLM models
  - GPT-4o
  - GPT-4o mini
  - o1-mini
  - More models coming soon

- **Real-Time Analytics**:
  - Brand mention frequency tracking
  - Position ranking analysis
  - Confidence scoring
  - Category distribution

- **Interactive Dashboard**:
  - Dynamic bar charts showing mentions vs. rankings
  - Brand ranking overview with favicon integration
  - Batch processing support
  - Real-time result updates

## Getting Started

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment:
```bash
export OPENAI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python main.py
```

## Usage

1. Enter your query in the terminal-style input
2. Select an AI model
3. Choose a category for better context
4. Set batch size (1-10 queries)
5. View real-time results and analytics

## Tech Stack

- **Backend**: Python/Flask
- **Database**: SQLite
- **Frontend**: HTML/JavaScript with TailwindCSS
- **Charts**: Chart.js
- **AI**: OpenAI API

## Key Features

### Brand Analysis
- Track brand mentions across queries
- Monitor ranking positions
- Analyze recommendation patterns
- Calculate confidence scores

### Real-Time Dashboard
- Top mentioned brands visualization
- Average ranking positions
- Category distribution
- Confidence metrics

### Query Processing
- Batch query support
- Multiple AI model options
- Category-based analysis
- Real-time updates

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
```

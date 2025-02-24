from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from datetime import datetime
import sqlite3
import os
import json

app = Flask(__name__)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

SYSTEM_PROMPT = """You are ChatGPT, a helpful AI assistant. Please format your brand recommendations as follows:
1. List the brand/company name
2. On a new line, provide the official website URL
3. On a new line, provide a brief (max 15 words) justification for why this brand was chosen
4. Separate each brand recommendation with '---'
    return render_template('index.html')
Example:
Nike
https://www.nike.com
Known for durability and innovation in athletic footwear, especially for running
---
Adidas
https://www.adidas.com
Strong reputation for comfortable everyday sneakers and athletic performance
---"""

def init_db():
    with sqlite3.connect('recommendations.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY,
                query TEXT,
                brands TEXT,
                urls TEXT,
                reasoning TEXT,
                rankings TEXT,
                timestamp DATETIME,
                category TEXT,
                model TEXT,
                confidence_score FLOAT
            )
        ''')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/reset-db', methods=['POST'])
def reset_db():
    try:
        os.remove('recommendations.db')
        init_db()
        return jsonify({"message": "Database reset successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    query = data.get('message', '')
    model = data.get('model', 'gpt-4')
    category = data.get('category', 'general')
    
    try:
        # Each request is a new conversation with just the system prompt and current query
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ]
        )
        
        content = response.choices[0].message.content
        recommendations = content.split('---')
        
        parsed_recommendations = []
        urls = []
        reasonings = []
        
        for rec in recommendations:
            if rec.strip():
                lines = rec.strip().split('\n')
                if len(lines) >= 3:
                    parsed_recommendations.append(lines[0].strip())
                    urls.append(lines[1].strip())
                    reasonings.append(lines[2].strip())

        # Calculate simple confidence score based on response consistency
        confidence_score = len(parsed_recommendations) / max(len(content.split()), 1)
        
        rankings = {}
        for idx, brand in enumerate(parsed_recommendations):
            rankings[brand] = idx + 1  # Store 1-based position

        with sqlite3.connect('recommendations.db') as conn:
            conn.execute(
                'INSERT INTO recommendations (query, brands, urls, reasoning, rankings, timestamp, category, model, confidence_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (query, json.dumps(parsed_recommendations), json.dumps(urls), json.dumps(reasonings), json.dumps(rankings), datetime.now(), category, model, confidence_score)
            )
        
        return jsonify({
            "brands": parsed_recommendations,
            "urls": urls,
            "reasoning": reasonings,
            "confidence_score": confidence_score,
            "timestamp": datetime.now().isoformat(),
            "category": category
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    with sqlite3.connect('recommendations.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            WITH RECURSIVE 
            brand_mentions AS (
                SELECT 
                    json_each.value as brand,
                    json_extract(urls, '$[' || json_each.key || ']') as url,
                    CAST(json_extract(rankings, '$.' || json_each.value) AS INTEGER) as position,
                    1 as mention_count
                FROM recommendations
                CROSS JOIN json_each(brands)
            ),
            brand_stats AS (
                SELECT 
                    brand,
                    COUNT(*) as total_mentions,
                    AVG(CASE WHEN position > 0 THEN position ELSE NULL END) as avg_position,
                    MAX(url) as url
                FROM brand_mentions
                GROUP BY brand
            )
            SELECT 
                brand,
                total_mentions as count,
                COALESCE(ROUND(avg_position, 1), 0) as avg_rank,
                url
            FROM brand_stats
            ORDER BY total_mentions DESC, avg_position ASC
            LIMIT 10
        ''')
        top_brands_data = cursor.fetchall()
        
        # Format the results
        top_brands = {
            row[0]: {
                'count': row[1],
                'avg_rank': row[2],
                'url': row[3]
            } for row in top_brands_data
        }
        
        # Get category distribution
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM recommendations 
            GROUP BY category
        ''')
        categories = cursor.fetchall()
        
        return jsonify({
            "top_brands": top_brands,
            "categories": dict(categories)
        })

# Add new endpoint for getting detailed analytics
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    with sqlite3.connect('recommendations.db') as conn:
        cursor = conn.cursor()
        
        # Get average confidence scores by category
        cursor.execute('''
            SELECT category, AVG(confidence_score) as avg_confidence
            FROM recommendations 
            GROUP BY category
        ''')
        confidence_by_category = dict(cursor.fetchall())
        
        # Get model usage statistics
        cursor.execute('''
            SELECT model, COUNT(*) as count
            FROM recommendations 
            GROUP BY model
        ''')
        model_usage = dict(cursor.fetchall())
        
        return jsonify({
            "confidence_by_category": confidence_by_category,
            "model_usage": model_usage
        })

@app.route('/api/ranking-analytics', methods=['GET'])
def ranking_analytics():
    with sqlite3.connect('recommendations.db') as conn:
        cursor = conn.execute('''
            SELECT brands, rankings
            FROM recommendations
            ORDER BY timestamp DESC
        ''')
        results = cursor.fetchall()
        
        brand_stats = {}
        for row in results:
            brands = json.loads(row[0])
            rankings = json.loads(row[1])
            
            for brand, rank in rankings.items():
                if brand not in brand_stats:
                    brand_stats[brand] = {
                        'mentions': 0,
                        'total_rank': 0,
                        'rank_history': []
                    }
                brand_stats[brand]['mentions'] += 1
                brand_stats[brand]['total_rank'] += rank
                brand_stats[brand]['rank_history'].append(rank)
        
        # Calculate average rankings
        for brand in brand_stats:
            brand_stats[brand]['avg_rank'] = brand_stats[brand]['total_rank'] / brand_stats[brand]['mentions']
            
        return jsonify(brand_stats)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
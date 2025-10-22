"""
GP4U Web API Server
Serves GPU pricing data to the frontend dashboard
"""
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import json
import asyncio
import sys
import os

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'integrations'))

from database import GP4UDatabase
from networks import GP4UNetworkAggregator

app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)

# Initialize components
db = GP4UDatabase('data/gp4u.db')

with open('config.json', 'r') as f:
    config = json.load(f)

aggregator = GP4UNetworkAggregator(config)

@app.route('/')
def index():
    """Serve the main dashboard"""
    return send_from_directory('web', 'index.html')

@app.route('/api/dashboard')
def get_dashboard():
    """Get dashboard statistics"""
    stats = db.get_dashboard_stats()
    return jsonify(stats)

@app.route('/api/gpus')
def get_gpus():
    """Get available GPU listings"""
    listings = db.get_recent_listings(100)
    return jsonify(listings)

@app.route('/api/gpus/cheapest')
def get_cheapest_gpus():
    """Get cheapest GPUs by model"""
    listings = db.get_recent_listings(100)
    
    # Group by model and find cheapest
    by_model = {}
    for listing in listings:
        if listing['availability'] != 'Available':
            continue
        model = listing['gpu_model']
        if model not in by_model or listing['total_price'] < by_model[model]['total_price']:
            by_model[model] = listing
    
    return jsonify(list(by_model.values()))

@app.route('/api/arbitrage')
def get_arbitrage():
    """Get arbitrage opportunities"""
    opportunities = db.get_recent_arbitrage(20)
    return jsonify(opportunities)

@app.route('/api/providers')
def get_providers():
    """Get provider statistics"""
    stats = db.get_provider_stats()
    return jsonify(stats)

@app.route('/api/models')
def get_models():
    """Get GPU model statistics"""
    stats = db.get_model_stats()
    return jsonify(stats)

@app.route('/api/refresh', methods=['POST'])
def trigger_refresh():
    """Manually trigger a data refresh"""
    async def do_refresh():
        gpus = await aggregator.fetch_all_gpus()
        gpu_dicts = [
            {
                'provider': g.provider,
                'gpu_model': g.gpu_model,
                'vram_gb': g.vram_gb,
                'price_per_hour': g.price_per_hour,
                'location': g.location,
                'availability': g.availability,
                'uptime_percent': g.uptime_percent,
                'provider_fee': g.provider_fee,
                'gp4u_fee': g.gp4u_fee,
                'total_price': g.total_price
            }
            for g in gpus
        ]
        db.save_gpu_listings(gpu_dicts)
        
        opportunities = aggregator.find_arbitrage_opportunities(gpus)
        if opportunities:
            opp_dicts = [
                {
                    'gpu_model': o.gpu_model,
                    'cheapest_provider': o.cheapest_provider,
                    'cheapest_price': o.cheapest_price,
                    'expensive_provider': o.expensive_provider,
                    'expensive_price': o.expensive_price,
                    'savings_percent': o.savings_percent,
                    'savings_amount': o.savings_amount
                }
                for o in opportunities
            ]
            db.save_arbitrage_opportunities(opp_dicts)
        
        return {'gpus': len(gpus), 'arbitrage': len(opportunities)}
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(do_refresh())
    loop.close()
    
    return jsonify({'status': 'success', 'data': result})

@app.route('/api/deployments', methods=['GET', 'POST'])
def handle_deployments():
    """Get or create deployments"""
    if request.method == 'GET':
        deployments = db.get_active_deployments()
        return jsonify(deployments)
    else:
        data = request.json
        deployment_id = db.create_deployment(
            data['provider'],
            data['gpu_model'],
            data['price_per_hour']
        )
        return jsonify({'status': 'success', 'deployment_id': deployment_id})

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 GP4U - WEB DASHBOARD")
    print("="*80)
    print("\nStarting web server...")
    print("Dashboard: http://localhost:5001")
    print("API: http://localhost:5001/api/dashboard")
    print("\nPress Ctrl+C to stop")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)

"""
GP4U - The Kayak of GPUs
Main orchestration engine
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'integrations'))

from networks import GP4UNetworkAggregator
from database import GP4UDatabase

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gp4u.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class GP4UEngine:
    def __init__(self, config_path: str = 'config.json'):
        """Initialize GP4U engine"""
        self.config = self._load_config(config_path)
        self.aggregator = GP4UNetworkAggregator(self.config)
        self.db = GP4UDatabase(self.config.get('database', {}).get('path', 'data/gp4u.db'))
        self.running = False
        
        logger.info("GP4U Engine initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    async def run_refresh_cycle(self):
        """Execute one refresh cycle"""
        logger.info("Starting refresh cycle...")
        
        # Fetch GPUs from all networks
        gpus = await self.aggregator.fetch_all_gpus()
        
        if not gpus:
            logger.warning("No GPUs fetched")
            return
        
        logger.info(f"Fetched {len(gpus)} GPUs from {len(set(g.provider for g in gpus))} providers")
        
        # Save to database
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
        self.db.save_gpu_listings(gpu_dicts)
        
        # Find arbitrage opportunities
        opportunities = self.aggregator.find_arbitrage_opportunities(gpus)
        
        if opportunities:
            logger.info(f"Found {len(opportunities)} arbitrage opportunities")
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
            self.db.save_arbitrage_opportunities(opp_dicts)
        
        # Display summary
        self._display_summary(gpus, opportunities)
    
    def _display_summary(self, gpus: List, opportunities: List):
        """Display cycle summary"""
        print(f"\n{'='*80}")
        print(f"📊 GP4U REFRESH SUMMARY - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")
        
        # Provider breakdown
        network_stats = self.aggregator.get_network_stats(gpus)
        print("\n🌐 Network Summary:")
        for provider, stats in network_stats.items():
            print(f"  {provider}: {stats['count']} GPUs | "
                  f"${stats['min_price']:.2f} - ${stats['max_price']:.2f}/hr")
        
        # Best deals
        available_gpus = [g for g in gpus if g.availability == 'Available']
        if available_gpus:
            cheapest = min(available_gpus, key=lambda x: x.total_price)
            print(f"\n💰 Best Deal: {cheapest.gpu_model} on {cheapest.provider}")
            print(f"   ${cheapest.total_price:.2f}/hr (Base: ${cheapest.price_per_hour:.2f} + Fees: ${cheapest.provider_fee + cheapest.gp4u_fee:.2f})")
        
        # Top arbitrage
        if opportunities:
            best = opportunities[0]
            print(f"\n📈 Top Arbitrage: {best.gpu_model}")
            print(f"   {best.cheapest_provider}: ${best.cheapest_price:.2f}/hr")
            print(f"   {best.expensive_provider}: ${best.expensive_price:.2f}/hr")
            print(f"   💵 Save {best.savings_percent:.1f}% (${best.savings_amount:.2f}/hr)")
        
        print(f"\n{'='*80}\n")
    
    async def run(self):
        """Main run loop"""
        self.running = True
        refresh_interval = self.config.get('refresh_interval_seconds', 60)
        
        print("\n" + "="*80)
        print("🚀 GP4U - The Kayak of GPUs")
        print("="*80)
        print("GPU Brokerage Platform - Compare • Deploy • Save")
        print(f"Refresh Interval: {refresh_interval} seconds")
        print("="*80 + "\n")
        
        cycle_count = 0
        
        try:
            while self.running:
                cycle_count += 1
                print(f"\n{'#'*80}")
                print(f"CYCLE {cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'#'*80}")
                
                await self.run_refresh_cycle()
                
                logger.info(f"Waiting {refresh_interval} seconds until next cycle...")
                await asyncio.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            logger.info("\nShutdown requested by user")
        finally:
            self._shutdown()
    
    def _shutdown(self):
        """Clean shutdown"""
        print("\n" + "="*80)
        print("📊 FINAL SUMMARY")
        print("="*80)
        
        stats = self.db.get_dashboard_stats()
        print(f"\nTotal Listings Tracked: {stats['total_listings']}")
        print(f"Average Price: ${stats['avg_price']:.2f}/hr")
        print(f"Cheapest GPU: ${stats['cheapest_gpu']:.2f}/hr")
        print(f"Arbitrage Opportunities: {stats['arbitrage_opportunities']}")
        if stats['best_arbitrage_percent'] > 0:
            print(f"Best Arbitrage: {stats['best_arbitrage_percent']:.1f}% savings")
        
        print("\n" + "="*80)
        print("🛑 GP4U Engine stopped")
        print("="*80)

async def main():
    """Main entry point"""
    print("\n🚀 GP4U - The Kayak of GPUs")
    print("="*80)
    print("Compare GPU prices across Render, Akash, io.net, Vast.ai")
    print("="*80)
    
    engine = GP4UEngine('config.json')
    await engine.run()

if __name__ == "__main__":
    asyncio.run(main())

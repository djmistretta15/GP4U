"""
GP4U Database - Track GPU listings, deployments, and pricing history
"""
import sqlite3
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GP4UDatabase:
    def __init__(self, db_path: str = 'data/gp4u.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # GPU listings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gpu_listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                gpu_model TEXT NOT NULL,
                vram_gb INTEGER,
                price_per_hour REAL,
                location TEXT,
                availability TEXT,
                uptime_percent REAL,
                provider_fee REAL,
                gp4u_fee REAL,
                total_price REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Arbitrage opportunities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gpu_model TEXT NOT NULL,
                cheapest_provider TEXT,
                cheapest_price REAL,
                expensive_provider TEXT,
                expensive_price REAL,
                savings_percent REAL,
                savings_amount REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Deployments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                gpu_model TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                price_per_hour REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                started_at DATETIME,
                stopped_at DATETIME,
                total_cost REAL DEFAULT 0
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                gpu_model TEXT NOT NULL,
                avg_price REAL,
                min_price REAL,
                max_price REAL,
                count INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_listings_timestamp ON gpu_listings(timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_listings_provider ON gpu_listings(provider)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_listings_model ON gpu_listings(gpu_model)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_arbitrage_timestamp ON arbitrage_opportunities(timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_deployments_status ON deployments(status)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized at {self.db_path}")
    
    def save_gpu_listings(self, listings: List[Dict]):
        """Save GPU listings to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for listing in listings:
            cursor.execute('''
                INSERT INTO gpu_listings (
                    provider, gpu_model, vram_gb, price_per_hour,
                    location, availability, uptime_percent,
                    provider_fee, gp4u_fee, total_price
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                listing['provider'],
                listing['gpu_model'],
                listing['vram_gb'],
                listing['price_per_hour'],
                listing['location'],
                listing['availability'],
                listing['uptime_percent'],
                listing['provider_fee'],
                listing['gp4u_fee'],
                listing['total_price']
            ))
        
        conn.commit()
        conn.close()
    
    def save_arbitrage_opportunities(self, opportunities: List[Dict]):
        """Save arbitrage opportunities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for opp in opportunities:
            cursor.execute('''
                INSERT INTO arbitrage_opportunities (
                    gpu_model, cheapest_provider, cheapest_price,
                    expensive_provider, expensive_price,
                    savings_percent, savings_amount
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                opp['gpu_model'],
                opp['cheapest_provider'],
                opp['cheapest_price'],
                opp['expensive_provider'],
                opp['expensive_price'],
                opp['savings_percent'],
                opp['savings_amount']
            ))
        
        conn.commit()
        conn.close()
    
    def get_recent_listings(self, limit: int = 100) -> List[Dict]:
        """Get recent GPU listings"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM gpu_listings 
            WHERE timestamp > datetime('now', '-1 hour')
            ORDER BY total_price ASC
            LIMIT ?
        ''', (limit,))
        
        listings = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return listings
    
    def get_recent_arbitrage(self, limit: int = 20) -> List[Dict]:
        """Get recent arbitrage opportunities"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM arbitrage_opportunities 
            WHERE timestamp > datetime('now', '-1 hour')
            ORDER BY savings_percent DESC
            LIMIT ?
        ''', (limit,))
        
        opportunities = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return opportunities
    
    def get_provider_stats(self) -> Dict:
        """Get statistics by provider"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                provider,
                COUNT(*) as count,
                AVG(total_price) as avg_price,
                MIN(total_price) as min_price,
                MAX(total_price) as max_price
            FROM gpu_listings 
            WHERE timestamp > datetime('now', '-1 hour')
            GROUP BY provider
        ''')
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = {
                'count': row[1],
                'avg_price': round(row[2], 2),
                'min_price': round(row[3], 2),
                'max_price': round(row[4], 2)
            }
        
        conn.close()
        return stats
    
    def get_model_stats(self) -> Dict:
        """Get statistics by GPU model"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                gpu_model,
                COUNT(*) as count,
                AVG(total_price) as avg_price,
                MIN(total_price) as min_price,
                MAX(total_price) as max_price
            FROM gpu_listings 
            WHERE timestamp > datetime('now', '-1 hour')
            GROUP BY gpu_model
        ''')
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = {
                'count': row[1],
                'avg_price': round(row[2], 2),
                'min_price': round(row[3], 2),
                'max_price': round(row[4], 2)
            }
        
        conn.close()
        return stats
    
    def get_dashboard_stats(self) -> Dict:
        """Get overall dashboard statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total listings
        cursor.execute('''
            SELECT COUNT(*) FROM gpu_listings 
            WHERE timestamp > datetime('now', '-1 hour')
        ''')
        total_listings = cursor.fetchone()[0]
        
        # Average price
        cursor.execute('''
            SELECT AVG(total_price) FROM gpu_listings 
            WHERE timestamp > datetime('now', '-1 hour')
        ''')
        avg_price = cursor.fetchone()[0] or 0.0
        
        # Cheapest GPU
        cursor.execute('''
            SELECT MIN(total_price) FROM gpu_listings 
            WHERE timestamp > datetime('now', '-1 hour') AND availability = 'Available'
        ''')
        cheapest = cursor.fetchone()[0] or 0.0
        
        # Arbitrage opportunities
        cursor.execute('''
            SELECT COUNT(*) FROM arbitrage_opportunities 
            WHERE timestamp > datetime('now', '-1 hour')
        ''')
        arbitrage_count = cursor.fetchone()[0]
        
        # Best arbitrage
        cursor.execute('''
            SELECT MAX(savings_percent) FROM arbitrage_opportunities 
            WHERE timestamp > datetime('now', '-1 hour')
        ''')
        best_arbitrage = cursor.fetchone()[0] or 0.0
        
        # Active providers
        cursor.execute('''
            SELECT COUNT(DISTINCT provider) FROM gpu_listings 
            WHERE timestamp > datetime('now', '-1 hour')
        ''')
        active_providers = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_listings': total_listings,
            'avg_price': round(avg_price, 2),
            'cheapest_gpu': round(cheapest, 2),
            'arbitrage_opportunities': arbitrage_count,
            'best_arbitrage_percent': round(best_arbitrage, 1),
            'active_providers': active_providers
        }
    
    def create_deployment(self, provider: str, gpu_model: str, price_per_hour: float) -> int:
        """Create a new deployment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO deployments (provider, gpu_model, price_per_hour, status)
            VALUES (?, ?, ?, 'pending')
        ''', (provider, gpu_model, price_per_hour))
        
        deployment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return deployment_id
    
    def update_deployment_status(self, deployment_id: int, status: str):
        """Update deployment status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status == 'running':
            cursor.execute('''
                UPDATE deployments 
                SET status = ?, started_at = datetime('now')
                WHERE id = ?
            ''', (status, deployment_id))
        elif status == 'stopped':
            cursor.execute('''
                UPDATE deployments 
                SET status = ?, stopped_at = datetime('now')
                WHERE id = ?
            ''', (status, deployment_id))
        else:
            cursor.execute('''
                UPDATE deployments 
                SET status = ?
                WHERE id = ?
            ''', (status, deployment_id))
        
        conn.commit()
        conn.close()
    
    def get_active_deployments(self) -> List[Dict]:
        """Get active deployments"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM deployments 
            WHERE status IN ('pending', 'running')
            ORDER BY created_at DESC
        ''')
        
        deployments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return deployments

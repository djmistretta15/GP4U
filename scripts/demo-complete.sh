#!/bin/bash

# Master Demo Script - Runs both GP4U and Lease Ledger demos
# Complete end-to-end demonstration in <5 minutes

set -e

echo "🚀 GP4U Complete MVP Demonstration"
echo "===================================="
echo ""
echo "This demo will showcase:"
echo "  1. GP4U Core - GPU arbitrage and marketplace"
echo "  2. Lease Ledger - Provenance tracking with blockchain"
echo ""
echo "Target completion time: <5 minutes"
echo ""

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
  echo "❌ Backend is not running!"
  echo ""
  echo "Please start the backend first:"
  echo "  cd backend"
  echo "  docker-compose up -d db redis"
  echo "  uvicorn app.main:app --reload"
  echo ""
  exit 1
fi

echo "✓ Backend is running"
echo ""

# Seed demo data
echo "📊 Seeding demo data..."
cd "$(dirname "$0")/.."
python3 scripts/seed_demo_data.py
echo ""

# Run GP4U demo
echo "===================="
echo "Part 1: GP4U Core"
echo "===================="
echo ""
./scripts/demo-golden-path.sh
echo ""

# Wait a moment
sleep 2

# Run Lease Ledger demo
echo "========================="
echo "Part 2: Lease Ledger"
echo "========================="
echo ""
./scripts/demo-lease-ledger.sh
echo ""

# Summary
echo "========================================"
echo "🎉 Complete MVP Demonstration Finished!"
echo "========================================"
echo ""
echo "✅ GP4U Core:"
echo "  - Multi-provider GPU search"
echo "  - Arbitrage opportunity detection"
echo "  - Best deal recommendation"
echo "  - GPU reservation booking"
echo ""
echo "✅ Lease Ledger:"
echo "  - GPU registration (dual-mode)"
echo "  - Provenance event tracking"
echo "  - Blockchain anchoring (SHA256)"
echo "  - Marketplace integration"
echo ""
echo "📱 Next Steps:"
echo "  1. Open frontend: http://localhost:3000"
echo "  2. Login with: demo@gp4u.com / demo123"
echo "  3. Explore Marketplace for arbitrage opportunities"
echo "  4. Click 'GPU Ledger' to see provenance tracking"
echo "  5. View API docs: http://localhost:8000/api/docs"
echo ""
echo "📚 Documentation:"
echo "  - Problem statements: docs/problem-*.md"
echo "  - API reference: docs/api.md"
echo "  - Architecture: docs/architecture.md"
echo "  - Validation plan: docs/validation.md"
echo ""
echo "🎯 Success Metrics:"
echo "  - GP4U: ≥20% cost savings, <2min search time"
echo "  - Lease Ledger: ≥80% dispute resolution time reduction"
echo ""

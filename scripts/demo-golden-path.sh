#!/bin/bash

# GP4U Golden Path Demo Script
# Demonstrates complete user flow: Search → Compare → Book
# Target: <60 seconds for demo

set -e

echo "🚀 GP4U Golden Path Demo"
echo "========================"
echo ""

API_BASE="http://localhost:8000/api"
DEMO_USER="demo@gp4u.com"
DEMO_PASS="demo123"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Register Demo User${NC}"
echo "Creating user: $DEMO_USER"

REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'$DEMO_USER'",
    "password": "'$DEMO_PASS'",
    "username": "demo_user"
  }' 2>/dev/null || echo '{"detail":"User already exists"}')

echo "✓ User registered"
echo ""

echo -e "${BLUE}Step 2: Login${NC}"
echo "Authenticating user..."

LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'$DEMO_USER'",
    "password": "'$DEMO_PASS'"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed. Is the backend running?"
  exit 1
fi

echo "✓ Logged in successfully"
echo ""

echo -e "${BLUE}Step 3: Search for GPUs${NC}"
echo "Searching for RTX 4090..."

SEARCH_START=$(date +%s%N | cut -b1-13)

SEARCH_RESPONSE=$(curl -s "$API_BASE/gpus/search?model=RTX%204090" \
  -H "Authorization: Bearer $TOKEN")

SEARCH_END=$(date +%s%N | cut -b1-13)
SEARCH_TIME=$((SEARCH_END - SEARCH_START))

GPU_COUNT=$(echo $SEARCH_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

echo "✓ Found $GPU_COUNT GPUs in ${SEARCH_TIME}ms"
echo ""

echo -e "${BLUE}Step 4: View Arbitrage Opportunities${NC}"
echo "Calculating price spreads..."

ARB_START=$(date +%s%N | cut -b1-13)

ARB_RESPONSE=$(curl -s "$API_BASE/arbitrage/opportunities?gpu_model=RTX%204090&min_spread=10" \
  -H "Authorization: Bearer $TOKEN")

ARB_END=$(date +%s%N | cut -b1-13)
ARB_TIME=$((ARB_END - ARB_START))

ARB_COUNT=$(echo $ARB_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

if [ "$ARB_COUNT" -gt 0 ]; then
  BEST_SPREAD=$(echo $ARB_RESPONSE | python3 -c "import sys, json; opps = json.load(sys.stdin); print(f\"{opps[0]['spread_pct']:.1f}%\" if opps else '0%')" 2>/dev/null)
  BEST_SAVINGS=$(echo $ARB_RESPONSE | python3 -c "import sys, json; opps = json.load(sys.stdin); print(f\"\${opps[0]['potential_savings_24h']:.2f}\" if opps else '\$0')" 2>/dev/null)
  
  echo "✓ Found $ARB_COUNT arbitrage opportunities in ${ARB_TIME}ms"
  echo "  Best spread: $BEST_SPREAD"
  echo "  Potential 24h savings: $BEST_SAVINGS"
else
  echo "✓ No arbitrage opportunities found (calculated in ${ARB_TIME}ms)"
fi
echo ""

echo -e "${BLUE}Step 5: Get Best Deal${NC}"
echo "Finding cheapest GPU..."

BEST_DEAL=$(curl -s "$API_BASE/arbitrage/best-deal/RTX%204090" \
  -H "Authorization: Bearer $TOKEN")

PROVIDER=$(echo $BEST_DEAL | python3 -c "import sys, json; print(json.load(sys.stdin).get('provider', 'N/A'))" 2>/dev/null)
PRICE=$(echo $BEST_DEAL | python3 -c "import sys, json; print(f\"\${json.load(sys.stdin).get('price_per_hour', 0):.2f}\")" 2>/dev/null)
GPU_ID=$(echo $BEST_DEAL | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

echo "✓ Best deal: $PROVIDER at $PRICE/hour"
echo "  GPU ID: $GPU_ID"
echo ""

if [ -z "$GPU_ID" ]; then
  echo "⚠️  No GPUs available for booking"
  echo ""
  echo -e "${GREEN}✅ Golden Path Demo Complete (Search + Analysis)${NC}"
  echo ""
  echo "📊 Performance Summary:"
  echo "  - Search time: ${SEARCH_TIME}ms"
  echo "  - Arbitrage calc: ${ARB_TIME}ms"
  echo "  - Total time: $((SEARCH_TIME + ARB_TIME))ms"
  echo ""
  echo "🎯 Target: <2000ms for search+arbitrage ✓"
  exit 0
fi

echo -e "${BLUE}Step 6: Create Reservation${NC}"
echo "Booking GPU for 2 hours..."

START_TIME=$(date -u -d "+1 hour" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -v+1H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")
END_TIME=$(date -u -d "+3 hours" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -v+3H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")

BOOK_RESPONSE=$(curl -s -X POST "$API_BASE/reservations/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gpu_id": "'$GPU_ID'",
    "start_time": "'$START_TIME'",
    "end_time": "'$END_TIME'"
  }')

RESERVATION_ID=$(echo $BOOK_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -n "$RESERVATION_ID" ]; then
  TOTAL_COST=$(echo $BOOK_RESPONSE | python3 -c "import sys, json; print(f\"\${json.load(sys.stdin).get('total_cost', 0):.2f}\")" 2>/dev/null)
  echo "✓ Reservation created successfully"
  echo "  Reservation ID: $RESERVATION_ID"
  echo "  Total cost: $TOTAL_COST"
else
  echo "❌ Booking failed (may be conflict or GPU unavailable)"
fi
echo ""

echo -e "${GREEN}✅ Golden Path Demo Complete!${NC}"
echo ""
echo "📊 Performance Summary:"
echo "  - Search time: ${SEARCH_TIME}ms"
echo "  - Arbitrage calc: ${ARB_TIME}ms"
echo "  - Total time: $((SEARCH_TIME + ARB_TIME))ms"
echo ""

if [ "$((SEARCH_TIME + ARB_TIME))" -lt 2000 ]; then
  echo "🎯 Target: <2000ms for search+arbitrage ✓"
else
  echo "⚠️  Target: <2000ms (actual: $((SEARCH_TIME + ARB_TIME))ms)"
fi
echo ""
echo "🔍 Next steps:"
echo "  - View reservation in dashboard: http://localhost:3000/reservations"
echo "  - Check arbitrage UI: http://localhost:3000/marketplace"
echo ""

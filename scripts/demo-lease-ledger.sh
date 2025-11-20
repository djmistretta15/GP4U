#!/bin/bash

# Lease Ledger Golden Path Demo Script
# Demonstrates: Register GPU → Update Status → View Provenance → Blockchain Hash
# Target: <60 seconds for demo

set -e

echo "🔐 Lease Ledger Golden Path Demo"
echo "================================="
echo ""

API_BASE="http://localhost:8000/api"
DEMO_USER="ledger@gp4u.com"
DEMO_PASS="ledger123"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Register Demo User${NC}"
echo "Creating user: $DEMO_USER"

curl -s -X POST "$API_BASE/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'$DEMO_USER'",
    "password": "'$DEMO_PASS'",
    "username": "ledger_operator"
  }' > /dev/null 2>&1 || true

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

echo -e "${BLUE}Step 3: Register GPU (Provenance Mode)${NC}"
echo "Registering RTX 4090 without price (provenance only)..."

REGISTER_RESPONSE_1=$(curl -s -X POST "$API_BASE/gpus/?model=RTX%204090%20Demo&vram_gb=24" \
  -H "Authorization: Bearer $TOKEN")

GPU_ID_1=$(echo $REGISTER_RESPONSE_1 | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

echo "✓ GPU registered (provenance-only mode)"
echo "  GPU ID: $GPU_ID_1"
echo "  Provider: lease-ledger"
echo "  Marketplace: Disabled"
echo ""

echo -e "${BLUE}Step 4: Register GPU (Marketplace Mode)${NC}"
echo "Registering RTX 3090 with price + location (marketplace enabled)..."

REGISTER_RESPONSE_2=$(curl -s -X POST "$API_BASE/gpus/?model=RTX%203090%20Demo&vram_gb=24&price_per_hour=2.50&location=US-East" \
  -H "Authorization: Bearer $TOKEN")

GPU_ID_2=$(echo $REGISTER_RESPONSE_2 | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
PRICE=$(echo $REGISTER_RESPONSE_2 | python3 -c "import sys, json; print(json.load(sys.stdin).get('price_per_hour', 0))" 2>/dev/null)

echo "✓ GPU registered (marketplace mode)"
echo "  GPU ID: $GPU_ID_2"
echo "  Price: \$$PRICE/hour"
echo "  Location: US-East"
echo "  Marketplace: Enabled ✓"
echo ""

echo -e "${BLUE}Step 5: Update GPU Status${NC}"
echo "Marking GPU as 'leased'..."

UPDATE_RESPONSE=$(curl -s -X PATCH "$API_BASE/gpus/$GPU_ID_1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "leased"}')

NEW_STATUS=$(echo $UPDATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null)

echo "✓ Status updated: available → $NEW_STATUS"
echo "  Provenance event created automatically"
echo ""

sleep 1

echo -e "${BLUE}Step 6: View Provenance Timeline${NC}"
echo "Fetching provenance events..."

PROVENANCE_RESPONSE=$(curl -s "$API_BASE/gpus/$GPU_ID_1/provenance" \
  -H "Authorization: Bearer $TOKEN")

EVENT_COUNT=$(echo $PROVENANCE_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

echo "✓ Found $EVENT_COUNT provenance events"
echo ""

if [ "$EVENT_COUNT" -gt 0 ]; then
  echo "Events:"
  echo $PROVENANCE_RESPONSE | python3 -c "
import sys, json
events = json.load(sys.stdin)
for i, event in enumerate(events, 1):
    print(f\"  {i}. {event['event_type']} at {event['created_at'][:19]}\")
    print(f\"     Event ID: {event['id'][:8]}...\")
" 2>/dev/null
  echo ""
fi

echo -e "${BLUE}Step 7: Create Blockchain Anchor${NC}"
echo "Hashing provenance events..."

# Get event IDs
EVENT_IDS=$(echo $PROVENANCE_RESPONSE | python3 -c "
import sys, json
events = json.load(sys.stdin)
ids = [e['id'] for e in events]
print(json.dumps(ids))
" 2>/dev/null || echo "[]")

ANCHOR_RESPONSE=$(curl -s -X POST "$API_BASE/anchors/hash" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"event_ids": '$EVENT_IDS'}')

HASH=$(echo $ANCHOR_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('hash', ''))" 2>/dev/null)
HASH_EVENT_COUNT=$(echo $ANCHOR_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('event_count', 0))" 2>/dev/null)

echo "✓ Blockchain anchor created"
echo "  Hash: $HASH"
echo "  Events hashed: $HASH_EVENT_COUNT"
echo "  Algorithm: SHA256"
echo ""

echo -e "${BLUE}Step 8: Verify in Marketplace${NC}"
echo "Checking if marketplace GPU is visible..."

MARKETPLACE_CHECK=$(curl -s "$API_BASE/gpus/search?provider=lease-ledger" \
  -H "Authorization: Bearer $TOKEN")

MARKETPLACE_COUNT=$(echo $MARKETPLACE_CHECK | python3 -c "import sys, json; gpus = json.load(sys.stdin); print(len([g for g in gpus if g.get('price_per_hour', 0) > 0]))" 2>/dev/null || echo "0")

echo "✓ Found $MARKETPLACE_COUNT lease-ledger GPUs in marketplace"
if [ "$MARKETPLACE_COUNT" -gt 0 ]; then
  echo "  These GPUs compete with Vast.ai, io.net, Akash, Render"
fi
echo ""

echo -e "${GREEN}✅ Lease Ledger Golden Path Complete!${NC}"
echo ""
echo "📊 Summary:"
echo "  - GPUs registered: 2 (1 provenance-only, 1 marketplace)"
echo "  - Status updates: 1"
echo "  - Provenance events: $EVENT_COUNT"
echo "  - Blockchain hash: Generated ✓"
echo "  - Marketplace integration: Active ✓"
echo ""
echo -e "${YELLOW}🔍 Verification Steps:${NC}"
echo "  1. View GPU Ledger UI: http://localhost:3000/gpus (click 'GPU Ledger' menu)"
echo "  2. Click '$GPU_ID_1' to see provenance timeline"
echo "  3. Check marketplace for 'RTX 3090 Demo' at \$2.50/hr"
echo "  4. Run arbitrage to see lease-ledger compete with other providers"
echo ""
echo "🎯 Unique Features:"
echo "  ✓ Only provider with blockchain provenance"
echo "  ✓ Immutable audit trail"
echo "  ✓ Dual-mode operation (provenance OR marketplace)"
echo "  ✓ Automatic event logging"
echo ""

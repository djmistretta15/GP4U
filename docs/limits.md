# Operating Limits & Constraints

## GP4U MVP - Operating Envelope

### Supported Scenarios (IN SCOPE)
✅ GPU search across 4 providers (Render, Akash, io.net, Vast.ai)
✅ Price comparison and arbitrage detection (15-40% spreads)
✅ Single GPU booking
✅ Multi-GPU cluster booking (2-8 GPUs)
✅ Time-block reservations (1 hour minimum)
✅ USDC wallet integration (deposit/withdraw)
✅ Real-time price sync (30-second intervals)
✅ Up to 100 concurrent users
✅ Provider health monitoring

### NOT Supported (OUT OF SCOPE for MVP)
❌ More than 8 GPUs in a single cluster
❌ Sub-hour time blocks
❌ Auto-renewal of reservations
❌ Multi-region cluster coordination
❌ Provider API failures lasting >5 minutes
❌ Custom GPU configurations
❌ Spot instance support
❌ More than 1000 GPUs in database

### Performance Limits

**Response Times:**
- Search results: <2 seconds
- Arbitrage calculation: <500ms
- Booking confirmation: <3 seconds
- Provider sync: <30 seconds

**Throughput:**
- Concurrent users: 100 max
- Searches per second: 50 max
- Bookings per minute: 20 max
- Database queries per second: 500 max

**Data Limits:**
- Max GPUs in database: 1,000
- Max reservations per user: 50 active
- Max cluster size: 8 GPUs
- History retention: 90 days

### Reliability Constraints

**Provider Dependency:**
- System requires ≥2 providers online
- If <2 providers available, show warning
- Graceful degradation: show available providers only
- No automatic failover to backup providers

**Data Freshness:**
- GPU data: Max 60 seconds stale
- Price data: Max 30 seconds stale
- Availability: Real-time with 30s sync

**Error Handling:**
- Provider timeout: 10 seconds max
- Retry attempts: 3 max with exponential backoff
- Circuit breaker: Open after 5 consecutive failures

### Known Limitations

1. **Provider API Rate Limits:**
   - Vast.ai: 100 requests/minute
   - io.net: 50 requests/minute
   - Akash: 60 requests/minute
   - Render: Not configured (unlimited for MVP)

2. **Arbitrage Accuracy:**
   - Prices cached for 30 seconds
   - Actual availability may differ during booking
   - Race conditions possible with high demand

3. **Cluster Coordination:**
   - No guarantee all GPUs in same location
   - Network latency between GPUs not measured
   - Manual coordination required for distributed training

4. **Blockchain Integration:**
   - USDC transactions on Ethereum/Polygon only
   - Gas fees not optimized
   - No batching of transactions

---

## Lease Ledger MVP - Operating Envelope

### Supported Scenarios (IN SCOPE)
✅ GPU registration (manual entry)
✅ Status tracking (available/leased/maintenance)
✅ Provenance event logging
✅ Blockchain anchor hashing (SHA256)
✅ Marketplace integration (optional pricing)
✅ Organization-level isolation
✅ Event timeline visualization
✅ Up to 1000 GPUs per organization

### NOT Supported (OUT OF SCOPE for MVP)
❌ Real blockchain integration (Ethereum/Polygon)
❌ Automated GPU discovery
❌ Hardware monitoring integration
❌ Automatic status updates from providers
❌ Smart contract execution
❌ Cross-organization visibility
❌ Bulk GPU import (>50 at once)
❌ NFT-based ownership

### Performance Limits

**Response Times:**
- GPU registration: <500ms
- Status update: <300ms
- Provenance query: <1 second
- Blockchain hash: <100ms

**Throughput:**
- GPUs per organization: 1,000 max
- Events per GPU: 10,000 max
- Status updates per minute: 100 max
- Concurrent users: 50 max

**Data Limits:**
- Max organizations: 100
- Max GPUs total: 10,000
- Event retention: Unlimited (but searchable for 1 year)
- JSON payload size: 10KB max

### Reliability Constraints

**Data Integrity:**
- Events are immutable once created
- No deletion of provenance events
- Status updates create new events (no overwrites)
- Blockchain hashes are deterministic

**Availability:**
- Database required (no offline mode)
- No event queuing (synchronous writes)
- Single point of failure (no replication for MVP)

**Error Handling:**
- Database errors: Return 500, no silent failures
- Invalid status transitions: Return 400 with explanation
- Duplicate hashes: Allowed (idempotent)

### Known Limitations

1. **Blockchain is Stub:**
   - SHA256 hashing only (not on-chain)
   - No smart contract integration
   - Hashes not published to blockchain
   - Manual verification required

2. **No Automated Discovery:**
   - All GPUs manually registered
   - No integration with provider APIs
   - Status updates are manual
   - No hardware health monitoring

3. **Organization Isolation:**
   - Organizations cannot see each other's GPUs
   - No marketplace across organizations
   - Admin cannot view all GPUs

4. **Marketplace Integration:**
   - Requires manual price entry
   - No dynamic pricing
   - No automatic price updates
   - Location must be manually specified

---

## System-Wide Constraints

### Infrastructure
- PostgreSQL 15+ required
- Redis required for caching
- Node 18+ for frontend
- Python 3.12+ for backend

### Security
- JWT tokens expire in 30 minutes
- Passwords must be 8+ characters
- No rate limiting on API (for MVP)
- CORS limited to localhost

### Deployment
- Docker Compose only (no Kubernetes)
- Single-region deployment
- No auto-scaling
- Manual backups only

### Monitoring
- Basic logging only
- No distributed tracing
- No APM integration
- Manual log review

---

## Graceful Degradation Strategies

### When Providers Fail
1. Show available providers only
2. Display warning about reduced coverage
3. Allow search with partial results
4. Suggest trying again later

### When Database is Slow
1. Increase cache TTL to 60 seconds
2. Show stale data with warning
3. Limit result set to 50 GPUs
4. Disable arbitrage calculation temporarily

### When Blockchain Hash Fails
1. Continue operation without hash
2. Log failure for manual review
3. Mark events as "unhashed"
4. Allow retry later

---

## Load Testing Recommendations

Before production:
- Test with 100 concurrent users
- Simulate provider failures
- Test database connection limits
- Verify cache expiration behavior
- Load test arbitrage calculation with 1000+ GPUs

---

## Upgrade Path (Post-MVP)

When limits are reached:
1. Implement horizontal scaling
2. Add provider-specific rate limiting
3. Implement queue for blockchain hashing
4. Add APM and distributed tracing
5. Implement auto-scaling policies
6. Add multi-region support

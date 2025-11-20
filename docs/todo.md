# TODO - Post-MVP Features

## GP4U Core - Next Steps

### High Priority (Next Sprint)

#### 1. Real Blockchain Integration
- [ ] Deploy USDC smart contract on Polygon testnet
- [ ] Implement wallet connect with MetaMask
- [ ] Add transaction signing
- [ ] Test end-to-end payment flow
- [ ] Add gas fee estimation

#### 2. Enhanced Arbitrage Algorithm
- [ ] Machine learning for price prediction
- [ ] Historical price trend analysis
- [ ] Predictive arbitrage opportunities
- [ ] Alert system for price drops
- [ ] Custom alert thresholds per user

#### 3. Advanced Cluster Management
- [ ] Auto-scaling clusters based on demand
- [ ] Cross-provider cluster coordination
- [ ] Network latency optimization
- [ ] GPU affinity rules
- [ ] Health monitoring for cluster nodes

#### 4. User Experience Improvements
- [ ] Saved search filters
- [ ] Favorite GPUs
- [ ] Price alert notifications
- [ ] Mobile-responsive improvements
- [ ] Onboarding tutorial
- [ ] Demo mode with sample data

### Medium Priority (Month 2-3)

#### 5. Provider Expansion
- [ ] Add Lambda Labs integration
- [ ] Add RunPod integration
- [ ] Add Paperspace integration
- [ ] Unified provider API abstraction layer
- [ ] Provider health dashboard

#### 6. Advanced Booking Features
- [ ] Recurring reservations
- [ ] Reservation templates
- [ ] Bulk booking discounts
- [ ] Reservation marketplace (resell bookings)
- [ ] Flexible cancellation policies

#### 7. Analytics & Reporting
- [ ] Cost savings dashboard
- [ ] Usage analytics per user
- [ ] Provider performance comparison
- [ ] Export reports (CSV, PDF)
- [ ] Custom date range analysis

#### 8. API Enhancements
- [ ] GraphQL API
- [ ] Webhook support for status changes
- [ ] API rate limiting
- [ ] API key management
- [ ] Public API documentation site

### Low Priority (Month 4-6)

#### 9. Enterprise Features
- [ ] Multi-user organizations
- [ ] Role-based access control (RBAC)
- [ ] Budget limits and approvals
- [ ] Invoice generation
- [ ] Dedicated account managers

#### 10. Advanced Search
- [ ] Natural language search
- [ ] AI-powered GPU recommendations
- [ ] Workload-specific suggestions
- [ ] Benchmark-based matching
- [ ] Similar GPU finder

#### 11. Community Features
- [ ] User reviews and ratings
- [ ] Provider reviews
- [ ] Community forum
- [ ] Tutorial marketplace
- [ ] Referral program

---

## Lease Ledger - Next Steps

### High Priority (Next Sprint)

#### 1. Real Blockchain Anchoring
- [ ] Replace SHA256 stub with Ethereum integration
- [ ] Deploy provenance smart contract
- [ ] On-chain event anchoring
- [ ] Block explorer integration
- [ ] Verification UI

#### 2. Automated Status Updates
- [ ] Integration with provider APIs
- [ ] Automatic status sync
- [ ] Health monitoring integration
- [ ] Availability detection
- [ ] Uptime calculation

#### 3. Enhanced Provenance Features
- [ ] Event categorization
- [ ] Custom event types
- [ ] Event search and filtering
- [ ] Event export (CSV, JSON)
- [ ] Audit report generation

### Medium Priority (Month 2-3)

#### 4. Marketplace Enhancements
- [ ] Dynamic pricing algorithm
- [ ] Demand-based price suggestions
- [ ] Seasonal pricing support
- [ ] Discount campaigns
- [ ] Featured listings

#### 5. Organization Management
- [ ] Multi-organization support
- [ ] Organization switching
- [ ] Organization-wide analytics
- [ ] Team member invitations
- [ ] Permission management

#### 6. Integration APIs
- [ ] Webhook callbacks for events
- [ ] Third-party integration SDKs
- [ ] Zapier integration
- [ ] CSV bulk import
- [ ] API documentation portal

### Low Priority (Month 4-6)

#### 7. NFT-Based Ownership
- [ ] GPU NFT minting
- [ ] NFT marketplace
- [ ] Transfer of ownership
- [ ] Fractional ownership
- [ ] Lease-to-own options

#### 8. Advanced Analytics
- [ ] Provenance analytics dashboard
- [ ] Dispute frequency tracking
- [ ] Revenue impact of provenance
- [ ] Customer trust metrics
- [ ] Compliance reporting

---

## Infrastructure & DevOps

### High Priority

#### 1. Production Deployment
- [ ] Set up production environment
- [ ] Configure CI/CD pipeline
- [ ] Automated testing in pipeline
- [ ] Blue-green deployment
- [ ] Rollback procedures

#### 2. Monitoring & Alerting
- [ ] Set up Prometheus + Grafana
- [ ] Define SLO/SLI metrics
- [ ] Alert routing (PagerDuty, Slack)
- [ ] Incident response playbook
- [ ] Status page

#### 3. Security Hardening
- [ ] Security audit
- [ ] Penetration testing
- [ ] OWASP compliance check
- [ ] Rate limiting implementation
- [ ] DDoS protection

### Medium Priority

#### 4. Performance Optimization
- [ ] Database query optimization
- [ ] Index tuning
- [ ] Caching strategy refinement
- [ ] CDN for static assets
- [ ] Image optimization

#### 5. Scalability
- [ ] Kubernetes migration
- [ ] Auto-scaling policies
- [ ] Database read replicas
- [ ] Redis cluster
- [ ] Load balancer configuration

#### 6. Disaster Recovery
- [ ] Automated backups
- [ ] Point-in-time recovery
- [ ] Cross-region replication
- [ ] Disaster recovery testing
- [ ] Data retention policies

---

## Documentation

### High Priority
- [ ] User onboarding guide
- [ ] Video tutorials
- [ ] FAQ section
- [ ] Troubleshooting guide
- [ ] API cookbook with examples

### Medium Priority
- [ ] Developer documentation
- [ ] Architecture decision records
- [ ] Contribution guidelines
- [ ] Code style guide
- [ ] Testing guidelines

---

## Testing

### High Priority
- [ ] Increase unit test coverage to 80%
- [ ] Add integration tests for all APIs
- [ ] End-to-end tests with Playwright
- [ ] Load testing with k6
- [ ] Security testing

### Medium Priority
- [ ] Contract testing for provider APIs
- [ ] Chaos engineering tests
- [ ] Performance regression tests
- [ ] Accessibility testing
- [ ] Cross-browser testing

---

## Compliance & Legal

### Medium Priority
- [ ] GDPR compliance review
- [ ] Privacy policy
- [ ] Terms of service
- [ ] Cookie consent
- [ ] Data processing agreements

### Low Priority
- [ ] SOC 2 certification
- [ ] ISO 27001 compliance
- [ ] Bug bounty program
- [ ] Responsible disclosure policy

---

## Features NOT in Scope (Explicitly Out)

These are features we consciously chose NOT to build:

❌ **Cryptocurrency mining** - Too controversial, high energy use
❌ **Spot instances** - Too complex for MVP, poor UX
❌ **Custom OS images** - Security risk, validation overhead
❌ **VPN/Networking setup** - Outside core value prop
❌ **Storage solutions** - Separate product category
❌ **Managed Kubernetes** - Too complex, many alternatives
❌ **AI model training service** - Different product
❌ **GPU hardware sales** - Not a marketplace feature
❌ **Insurance for bookings** - Legal complexity

---

## Decision Log

**Why we're NOT adding these features:**

1. **Auto-renewal:** Increases billing disputes, adds complexity
2. **Multi-region clusters:** Network latency issues, user can coordinate manually
3. **Spot instances:** Price volatility creates poor UX
4. **Custom ML frameworks:** Too many permutations, let users install
5. **Built-in notebooks:** Jupyter not our core competency

---

## Prioritization Framework

**How we prioritize:**

1. **User Impact:** Does it solve a validated pain point?
2. **Business Value:** Does it increase revenue or retention?
3. **Effort:** What's the engineering cost?
4. **Risk:** What could go wrong?

**Formula:**
```
Priority Score = (User Impact × Business Value) / (Effort × Risk)
```

Top score = do first

---

## Success Metrics for Next Features

Each feature above should define:
- Primary success metric
- Numeric target
- Measurement method
- Timeline for evaluation

Example:
**Feature:** Saved search filters
**Metric:** % of users who save ≥1 filter
**Target:** ≥40% within 30 days of launch
**Measurement:** Track "save_filter" events
**Evaluation:** Week 5 after launch

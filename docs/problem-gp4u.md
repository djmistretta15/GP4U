# Problem Statement: GP4U MVP

## Clear Problem Statement

GPU users (developers, ML engineers, researchers) waste **15-40% on GPU rental costs** because they manually search across multiple cloud providers (Render, Akash, io.net, Vast.ai) without knowing which offers the best price for their specific needs.

## Target Persona + Pain Points

**Primary Persona:** Alex, ML Engineer at a startup
- **Role:** Training neural networks for computer vision
- **Budget:** $500-2000/month for GPU compute
- **Pain Points:**
  1. Checks 4+ websites manually to compare GPU prices
  2. Spends 30-60 minutes per job finding cheapest option
  3. Misses arbitrage opportunities (price differences up to 40%)
  4. No visibility into real-time availability
  5. Difficult to book time blocks or multi-GPU clusters

**Secondary Persona:** Maria, Freelance Data Scientist
- **Budget:** Limited project-based spending
- **Pain Points:**
  1. Needs cheapest option but lacks time to research
  2. Wants reliable GPUs with good uptime
  3. Needs simple reservation system

## Frequency + Current Workaround

**Frequency:** 
- Alex: 10-20 GPU jobs per month
- Maria: 3-5 GPU jobs per month
- Average time wasted: 45 minutes per search × 15 jobs = **11.25 hours/month**

**Current Workaround:**
1. Open 4 tabs (Render, Akash, io.net, Vast.ai)
2. Manually search for GPU model (e.g., RTX 4090)
3. Copy prices to spreadsheet
4. Calculate which is cheapest
5. Go to cheapest provider and book
6. Repeat for every job

## Why Current Workaround is Inadequate

1. **Time-consuming:** 45 min × 15 searches = 11.25 hours wasted monthly
2. **Error-prone:** Manual comparison leads to mistakes
3. **Misses opportunities:** Prices change; by the time comparison is done, deal may be gone
4. **No historical data:** Can't learn from past choices
5. **No automation:** Every search is manual from scratch
6. **No multi-GPU support:** Complex to coordinate clusters across providers

## Falsifiable Hypothesis (H₁)

**H₁:** If we provide a single interface that automatically compares GPU prices across 4+ providers in real-time and highlights the cheapest option, users will:
- Save **≥20%** on average GPU costs
- Reduce search time from 45 minutes to **<2 minutes**
- Book GPUs **≥3x faster** than manual process

**Measurable Outcomes:**
- Cost savings: Track actual booking price vs. average market price
- Time savings: Measure search-to-book duration
- Booking frequency: Users book more often due to reduced friction

## Null Hypothesis (H₀)

**H₀:** Providing automated price comparison will NOT result in:
- ≥20% cost savings
- <2 minute search time
- ≥3x faster booking

**Rejection Criteria:** If even ONE of the three metrics is not met after 30 user sessions, H₀ is not rejected.

## Primary Success Metric with Numeric Target

**Primary Metric:** **Average Cost Savings Per Booking**

**Target:** ≥ 20% savings

**Measurement:**
```
Savings % = (Market_Avg_Price - GP4U_Booking_Price) / Market_Avg_Price × 100
```

**Success Condition:** 
- 70% of bookings achieve ≥20% savings
- Measured over minimum 30 bookings
- Compared against same-day average prices from all 4 providers

**Secondary Metrics:**
1. **Time to Book:** <2 minutes (from search to booking confirmation)
2. **Booking Frequency:** 3x increase in user booking rate vs. manual process
3. **User Retention:** 60% of users return for 2nd booking within 30 days

## Data Collection Plan

1. **Cost Savings:** Log booking price + market average at booking time
2. **Time Savings:** Track timestamp of search start and booking confirmation
3. **Booking Frequency:** User ID + booking count over time periods
4. **User Retention:** Track user return visits

## Validation Timeline

- **Week 1-2:** Deploy MVP, collect baseline data
- **Week 3-4:** Analyze first 30 bookings
- **Week 5:** Evaluate H₁ vs. H₀, decide pivot or persevere

## Risk Mitigation

**Risk:** Users don't trust automated comparison
**Mitigation:** Show all provider prices transparently, let users verify

**Risk:** Providers change prices too frequently
**Mitigation:** Cache for 30 seconds, show "last updated" timestamp

**Risk:** Users prefer specific providers (trust/loyalty)
**Mitigation:** Allow filtering by preferred provider while still showing savings

## Definition of MVP Success

MVP is considered **successful** if:
1. ✅ ≥20% average cost savings achieved
2. ✅ <2 minute average time to book
3. ✅ ≥60% user retention for 2nd booking
4. ✅ No silent failures in arbitrage calculation
5. ✅ System handles ≥100 concurrent users

**Failure Condition:** If any core metric fails after 30 bookings, pivot strategy.

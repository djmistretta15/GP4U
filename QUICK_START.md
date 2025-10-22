# 🚀 GP4U - QUICK START GUIDE

## Get Running in 3 Steps

### Step 1: Install
```bash
cd gp4u
pip install -r requirements.txt --break-system-packages
```

### Step 2: Start Web Dashboard
```bash
./start_web.sh
```

### Step 3: Open Browser
```
http://localhost:5001
```

**That's it!** You'll see GPU prices from 4 networks.

---

## First Time Setup

If the dashboard is empty:

1. **Start the price engine** (Terminal 1):
   ```bash
   python3 main.py
   ```

2. **Wait 60 seconds** for first refresh cycle

3. **Start web dashboard** (Terminal 2):
   ```bash
   ./start_web.sh
   ```

4. **Open browser**: http://localhost:5001

---

## What You'll See

### Dashboard Stats
- 💻 **GPUs Available**: Total across all networks
- 💰 **Average Price**: Mean price per hour
- 🎯 **Best Deal**: Cheapest GPU available
- 📈 **Arbitrage**: Best savings opportunity

### GPU Listings
Each card shows:
- GPU model and VRAM
- Provider (Render, Akash, io.net, Vast.ai)
- Location and uptime
- Complete price breakdown with fees
- Total price per hour

### Arbitrage Opportunities
See side-by-side comparisons:
- Cheapest provider vs most expensive
- Exact savings amount
- Percentage difference

---

## Controls

### Filter by Provider
Click: `All` | `Render` | `Akash` | `io.net` | `Vast.ai`

### Sort Options
Click: `Price` | `Uptime` | `VRAM`

### Refresh Prices
Click: `🔄 Refresh Prices`

---

## Example: Finding Best GPU

**Goal**: Find cheapest RTX 4090

1. Open http://localhost:5001
2. GPU listings auto-sorted by price
3. Look for "RTX 4090" cards
4. Compare providers and fees
5. Choose best total price

**Result**: Save 20-40% vs going direct to one provider!

---

## Troubleshooting

### No GPUs showing?
```bash
# Start engine to populate database
python3 main.py
# Wait 60 seconds
# Refresh browser
```

### Can't connect?
```bash
# Check server is running
curl http://localhost:5001/api/dashboard

# Restart server
./start_web.sh
```

### Port already in use?
Edit `web_server.py` line 95:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

---

## API Quickstart

### Get All GPUs
```bash
curl http://localhost:5001/api/gpus
```

### Get Dashboard Stats
```bash
curl http://localhost:5001/api/dashboard
```

### Get Arbitrage Opportunities
```bash
curl http://localhost:5001/api/arbitrage
```

### Trigger Price Refresh
```bash
curl -X POST http://localhost:5001/api/refresh
```

---

## Pro Tips

1. **Run engine continuously** for real-time price tracking
2. **Sort by price** to find best deals immediately  
3. **Check arbitrage section** for biggest savings
4. **Filter by provider** to compare specific networks
5. **Use API** to integrate with your own tools

---

## Key Features

✅ **Real-time pricing** from 4 GPU networks  
✅ **Transparent fees** - see exactly what you pay  
✅ **Arbitrage detection** - up to 40% savings  
✅ **Beautiful dashboard** - easy to use  
✅ **REST API** - integrate anywhere  
✅ **One-click refresh** - latest prices instantly  

---

## Quick Command Reference

```bash
# Start web dashboard
./start_web.sh

# Start price engine
python3 main.py

# Check if server is running
curl http://localhost:5001/api/dashboard

# View all GPUs
curl http://localhost:5001/api/gpus | jq

# Monitor arbitrage
watch -n 30 'curl -s http://localhost:5001/api/arbitrage | jq ".[0]"'
```

---

## Next Steps

1. ✅ Explore the dashboard
2. ✅ Compare prices across providers
3. ✅ Find arbitrage opportunities
4. ✅ Use API for automation
5. ✅ Save money on GPU compute!

---

**Your GPU marketplace is ready! Start comparing prices now.**

**Dashboard**: http://localhost:5001

# NFT Floor Price Tracker

Automated daily tracking of Solana NFT floor prices using GitHub Actions.

## 📊 What This Does

- Tracks floor prices for popular Solana NFT collections
- Runs automatically every day at 2 AM UTC via GitHub Actions
- Builds 30-day historical averages
- Database is committed to repo after each run

## 🚀 Usage

### Get Latest Data
```bash
git pull
```

### View Statistics
```bash
python track_floors.py --stats
```

### Manual Run
```bash
python track_floors.py
```

## 📈 Collections Tracked

See COLLECTIONS list in `track_floors.py`

## 🔧 Setup

1. Push this repo to GitHub
2. Enable GitHub Actions
3. Manual first run or wait for scheduled run
4. Database builds over 30 days

## 📊 Database

`nft_floors.db` contains daily floor prices
- After 7 days: Use 7-day averages
- After 30 days: Use 30-day averages

## 🌐 Accessibility

Database is public and free to use!

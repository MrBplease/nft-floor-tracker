#!/usr/bin/env python3
"""Daily Floor Price Tracker for Solana NFTs"""
import requests
import sqlite3
from datetime import datetime
import sys

COLLECTIONS = [
    "degods", "okay_bears", "mad_lads", "tensorians",
    "smb_gen2", "famous_fox_federation", "abc", "claynosaurz",
    "degenerate_ape_academy", "solana_monkey_business"
]

MAGIC_EDEN_URL = "https://api-mainnet.magiceden.dev/v2"
DATABASE = "nft_floors.db"

def init_database():
    conn = sqlite3.connect(DATABASE)
    conn.execute('''CREATE TABLE IF NOT EXISTS floor_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        collection TEXT NOT NULL,
        floor_price REAL NOT NULL,
        volume_24h REAL, volume_7d REAL, volume_all REAL,
        listed_count INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(collection, DATE(timestamp)))'''
    )
    conn.execute('''CREATE INDEX IF NOT EXISTS idx_collection_date 
        ON floor_history(collection, timestamp DESC)'''
    )
    conn.commit()
    return conn

def get_stats(collection):
    try:
        url = f"{MAGIC_EDEN_URL}/collections/{collection}/stats"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except: return None

def track_floors():
    conn = init_database()
    ts = datetime.now()
    print(f"\n{'='*60}\nTracking Floor Prices - {ts.strftime('%Y-%m-%d %H:%M:%S')}\n{'='*60}\n")
    success = 0
    for col in COLLECTIONS:
        print(f"Fetching: {col}...", end=" ")
        stats = get_stats(col)
        if stats:
            floor = float(stats.get('floorPrice', 0)) / 1e9
            vol24 = float(stats.get('volume24hr', 0)) / 1e9
            vol7 = float(stats.get('volume7d', 0)) / 1e9
            volAll = float(stats.get('volumeAll', 0)) / 1e9
            listed = int(stats.get('listedCount', 0))
            try:
                conn.execute('''INSERT OR REPLACE INTO floor_history 
                    (collection, floor_price, volume_24h, volume_7d, volume_all, listed_count, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (col, floor, vol24, vol7, volAll, listed, ts))
                print(f"✓ {floor:.4f} SOL")
                success += 1
            except: print(f"✗ DB Error")
        else: print(f"✗ Failed")
    conn.commit()
    conn.close()
    print(f"\n{'='*60}\nTracked {success}/{len(COLLECTIONS^)} collections\n{'='*60}\n")

def show_stats():
    conn = sqlite3.connect(DATABASE)
    print(f"\n{'='*60}\nFloor Price Tracking Statistics\n{'='*60}\n")
    for col in COLLECTIONS:
        days = conn.execute('SELECT COUNT(DISTINCT DATE(timestamp)) FROM floor_history WHERE collection=?', (col,)).fetchone()[0]
        if days == 0: print(f"{col:30} No data yet"); continue
        latest = conn.execute('SELECT floor_price, timestamp FROM floor_history WHERE collection=? ORDER BY timestamp DESC LIMIT 1', (col,)).fetchone()
        avg7 = conn.execute('SELECT AVG(floor_price) FROM floor_history WHERE collection=? AND timestamp >= datetime("now", "-7 days")', (col,)).fetchone()[0]
        avg30 = conn.execute('SELECT AVG(floor_price) FROM floor_history WHERE collection=? AND timestamp >= datetime("now", "-30 days")', (col,)).fetchone()[0]
        print(f"{col:30} {days:2} days\n  Current: {latest[0]:.4f} SOL")
        if avg7: print(f"  7d Avg:  {avg7:.4f} SOL")
        if avg30: print(f"  30d Avg: {avg30:.4f} SOL")
        print()
    conn.close()

if __name__ == "__main__":
    if "--stats" in sys.argv: show_stats()
    else: track_floors()

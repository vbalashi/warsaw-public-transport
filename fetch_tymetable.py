import asyncio
import aiohttp
import pandas as pd
import os
import time
import json
from aiohttp import ClientError
import logging

# ------------------------------------------------------------------
# 1) CONFIGURATION
# ------------------------------------------------------------------
API_URL = "https://api.um.warszawa.pl/api/action/dbtimetable_get"
API_ID = "e923fa0e-d96c-43f9-ae6e-60518c9f3238"  # Provided "id" param
QPS = 5               # queries per second
MAX_RETRIES = 3       # max number of retries on failure
OUTPUT_FOLDER = "data/timetable"
CSV_FILENAME = "data/df_bus_routes.csv"  # your CSV file
# If the API also needs an 'apikey' param, add it here:
API_KEY = "op://khrustal/api.um.warszawa.pl/Section_j3dttihdrs6or7g7eztj2zaeuq/api_key"
# ------------------------------------------------------------------
# 2) PREPARE OUTPUT FOLDER & DATAFRAME
# ------------------------------------------------------------------
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

df = pd.read_csv(CSV_FILENAME)

# We only need columns: line, bus_stop_group, bus_stop_platform
# Group them so we fetch each unique combination once
grouped = df.groupby(['line', 'bus_stop_group', 'bus_stop_platform']).size().reset_index()
total_tasks = len(grouped)

# For progress tracking
completed_tasks = 0
start_time = time.time()

# ------------------------------------------------------------------
# 3) RATE LIMITER
# ------------------------------------------------------------------
class RateLimiter:
    """Simple token bucket rate limiter for QPS control."""
    def __init__(self, rate, loop=None):
        self.rate = rate
        self.tokens = rate
        # Modern way to handle event loops
        if loop is None:
            try:
                self.loop = asyncio.get_running_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
        else:
            self.loop = loop
        self.last = self.loop.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        async with self._lock:
            now = self.loop.time()
            elapsed = now - self.last
            # Refill tokens based on time passed
            self.tokens += elapsed * self.rate
            if self.tokens > self.rate:
                self.tokens = self.rate
            if self.tokens < 1:
                # Need to wait for a token
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                now = self.loop.time()
                elapsed = now - self.last
                self.tokens += elapsed * self.rate
            # Consume one token
            self.tokens -= 1
            self.last = now

rate_limiter = RateLimiter(QPS)

# ------------------------------------------------------------------
# 4) API FETCH FUNCTION
# ------------------------------------------------------------------
async def fetch_timetable(session, line, busstopId, busstopNr):
    """Fetch data from the API with retries and rate-limiting."""
    # Format line and both bus stop values as strings with leading zeros
    line_str = str(line).strip()
    busstopId_str = str(busstopId).zfill(4)  # Assuming 4 digits for busstopId
    busstopNr_str = str(busstopNr).zfill(2)
    
    params = {
        "id": API_ID,
        "busstopId": busstopId_str,
        "busstopNr": busstopNr_str,
        "line": line_str,
        "apikey": API_KEY,  # Uncommented - try with API key
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            await rate_limiter.acquire()
            async with session.get(API_URL, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    response_text = await response.text()
                    print(f"[Attempt {attempt}] HTTP {response.status} for line={line_str},"
                          f" busstopId={busstopId_str}, busstopNr={busstopNr_str}")
                    print(f"Response: {response_text[:200]}...")  # Show part of the response
        except Exception as e:
            print(f"[Attempt {attempt}] Exception {type(e).__name__}: {str(e)} for line={line_str},"
                  f" busstopId={busstopId_str}, busstopNr={busstopNr_str}")
        
        # Exponential backoff
        await asyncio.sleep(2 ** attempt)

    return None

# ------------------------------------------------------------------
# 5) PROCESS ONE ROW
# ------------------------------------------------------------------
async def process_row(session, row):
    """Process a single unique combination (line, busstopId, busstopNr)."""
    global completed_tasks

    line = row['line']
    busstopId = row['bus_stop_group']
    busstopNr = row['bus_stop_platform']
    
    # Format strings for filename - keep the original values for the API call
    line_str = str(line).strip()
    busstopId_str = str(busstopId).zfill(4)  # Assuming 4 digits for busstopId
    busstopNr_str = str(busstopNr).zfill(2)
    
    # Example: "118_0302_01.json"
    filename = f"{line_str}_{busstopId_str}_{busstopNr_str}.json"
    filepath = os.path.join(OUTPUT_FOLDER, filename)

    # Skip if file exists
    if os.path.exists(filepath):
        completed_tasks += 1
        elapsed = time.time() - start_time
        print(f"Skipping existing {filename}  ({completed_tasks}/{total_tasks}, {elapsed:.1f}s)")
        return

    # Pass the original values, the fetch_timetable function will format them
    data = await fetch_timetable(session, line, busstopId, busstopNr)
    if data is None:
        print(f"Failed after retries: {filename}")
    else:
        # Check if unauthorized
        if data.get("result") == "false" and data.get("error") == "Nieautoryzowany dostęp do danych":
            print(f"Unauthorized response for {filename}, skipping save.")
        else:
            # Save to JSON
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Saved {filename}")

    completed_tasks += 1
    elapsed = time.time() - start_time
    print(f"Progress: {completed_tasks}/{total_tasks} | Elapsed: {elapsed:.2f}s")

# ------------------------------------------------------------------
# 6) MAIN ASYNC RUN
# ------------------------------------------------------------------
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _, row in grouped.iterrows():
            tasks.append(process_row(session, row))
        await asyncio.gather(*tasks)

# ------------------------------------------------------------------
# 7) ENTRY POINT WITH Ctrl+C HANDLING
# ------------------------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting gracefully.")

# Add at the top of the file, after imports
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_debug.log'
)
logger = logging.getLogger('warsaw_api')

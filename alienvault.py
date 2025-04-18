import csv
import sys
from OTXv2 import OTXv2
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# === CONFIGURATION ===
API_KEY = 'YOUR_API_KEY_GOE_HERE'
MAX_INDICATORS = 300000  # Max number of indicators to collect per search term
MAX_WORKERS = 30         # ThreadPool concurrency (lower this if you experience slowdowns)
RATE_LIMIT_DELAY = 0.1   # Delay between API calls
max_results = 1000       # Max number of pulses to fetch per term (a pulse may contain 50 or 5000 indicators, you never know!)

# === FUNCTIONS ===
def fetch_pulse_details(otx, pulse):
    try:
        details = otx.get_pulse_details(pulse['id'])
        return pulse, details.get('indicators', [])
    except Exception as e:
        print(f"Error fetching pulse {pulse['id']}: {e}")
        return pulse, []

def search_all_pulses(otx, search_term, max_indicators):
    all_pulses = []
    unique_indicators = set()

    # Fetch up to N pulses using built-in pagination
    print(f"Searching pulses for: {search_term}")
    try:
        results = otx.search_pulses(search_term, max_results)  # adjust as needed
    except Exception as e:
        print(f"Error fetching pulses: {e}")
        return []

    if not results:
        print("No results found.")
        return []

    # Sort pulses by modified date
    sorted_pulses = sorted(
        results.get('results', results),  # depending on SDK version
        key=lambda p: datetime.strptime(p.get('modified', '1970-01-01T00:00:00.000000'), "%Y-%m-%dT%H:%M:%S.%f"),
        reverse=True
    )

    for pulse in sorted_pulses:
        try:
            indicators = otx.get_pulse_details(pulse['id']).get('indicators', [])
        except Exception as e:
            print(f"Error fetching indicators for pulse {pulse['id']}: {e}")
            continue

        for ind in indicators:
            unique_indicators.add(ind.get('indicator', ''))
            if len(unique_indicators) >= max_indicators:
                print(f"Reached {max_indicators} unique indicators.")
                return all_pulses

        all_pulses.append((pulse, indicators))

    return all_pulses

def get_related_pulses(pulse_data):
    return [r.get('name', '') for r in pulse_data.get('related', {}).get('pulses', [])]

def export_indicators_to_csv(pulses, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([
            'Pulse Name', 'Pulse ID', 'Indicator Type', 'Indicator', 'Roles',
            'Title', 'Date Added', 'Active', 'Related Pulses'
        ])

        seen_indicators = set()
        for pulse, indicators in pulses:
            pulse_id = pulse.get('id')
            pulse_name = pulse.get('name')
            related_pulses = get_related_pulses(pulse)

            for ind in indicators:
                indicator_value = ind.get('indicator', '')
                if indicator_value in seen_indicators:
                    continue
                seen_indicators.add(indicator_value)

                try:
                    writer.writerow([
                        pulse_name,
                        pulse_id,
                        ind.get('type', ''),
                        indicator_value,
                        ','.join(ind.get('role', [])) if isinstance(ind.get('role'), list) else ind.get('role', ''),
                        ind.get('title', ''),
                        ind.get('created', ''),
                        ind.get('is_active', ''),
                        ', '.join(related_pulses)
                    ])
                except Exception as e:
                    print(f"⚠️ Skipped problematic row (indicator: {indicator_value}) due to error: {e}")
                    continue

                if len(seen_indicators) >= MAX_INDICATORS:
                    return len(seen_indicators)

        return len(seen_indicators)


# === MAIN ===

def main():
    if len(sys.argv) < 2:
        print("Usage: python alienvaultv3.py <search_term1> [<search_term2> ...]")
        sys.exit(1)

    search_terms = sys.argv[1:]
    otx = OTXv2(API_KEY)

    for search_term in search_terms:
        print(f"\nSearching for: {search_term}")
        start_time = time.time()

        pulses = search_all_pulses(otx, search_term, MAX_INDICATORS)

        if not pulses:
            print(f"No pulses found for '{search_term}'")
            continue

        filename = f"{search_term}_indicators.csv"
        unique_count = export_indicators_to_csv(pulses, filename)

        elapsed_time = time.time() - start_time
        print(f"Saved {unique_count} unique indicators from {len(pulses)} pulses to '{filename}' in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()

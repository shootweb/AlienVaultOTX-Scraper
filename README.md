# AlienVault OTX Pulse Indicator Extractor

This Python script connects to [AlienVault OTX](https://otx.alienvault.com/) using the OTXv2 API and retrieves indicators of compromise (IOCs) from threat intelligence pulses based on user-defined search terms. It exports these indicators to CSV files for further analysis.

## Features

- Fetches pulses related to one or more search terms
- Retrieves and deduplicates IOCs from each pulse
- Handles pagination and rate limiting
- Outputs clean CSV reports with indicator metadata
- Multithreaded fetching with configurable concurrency

## Requirements

- Python 3.6+
- [OTXv2 Python SDK](https://github.com/AlienVault-OTX/OTX-Python-SDK)

Install dependencies using:

```
pip install OTXv2
```

## Configuration

Open the script and edit the following constants at the top:

```
API_KEY = 'YOUR_API_KEY_GOES_HERE'
MAX_INDICATORS = 300000  # Max number of indicators to collect per search term
MAX_WORKERS = 30         # ThreadPool concurrency (lower this if you experience slowdowns)
RATE_LIMIT_DELAY = 0.1   # Delay between API calls
max_results = 1000       # Max number of pulses to fetch per term
```

Get your OTX API key from: `https://otx.alienvault.com/api`

## Usage

Run the script with one or more search terms:

```
python alienvaultv4.py ransomware phishing "Cobalt Strike"
```

Each search term will produce a separate CSV file named:

```
<search_term>_indicators.csv
```

## Example

```
python alienvaultv4.py FIN6 Magecart
```

This will generate:
- `FIN6_indicators.csv`
- `Magecart_indicators.csv`

Each file will contain the most recent 300,000 unique indicators from related OTX pulses.

## Output CSV Fields

Each row in the output CSV contains:

- `Pulse Name`: Name of the pulse
- `Pulse ID`: Unique ID of the pulse
- `Indicator Type`: Type of IOC (e.g., domain, IP, URL, hash)
- `Indicator`: The actual IOC value
- `Roles`: Role(s) the indicator plays (if available)
- `Title`: Indicator title
- `Date Added`: When the indicator was added
- `Active`: Indicator active status
- `Related Pulses`: Comma-separated names of related pulses

CSV is encoded in UTF-8 and uses `;` as the field delimiter.

## How It Works

1. Uses `search_pulses()` to fetch a batch of pulse summaries for a term.
2. Fetches full pulse details (including indicators) using `get_pulse_details()`.
3. Deduplicates indicators and tracks unique IOCs.
4. Saves results into a CSV with metadata for each indicator.

## Notes

- API rate limits may affect performance.
- Avoid excessively high values for `MAX_WORKERS` or `MAX_INDICATORS` on slower machines.
- Duplicate indicators across pulses are filtered automatically.
- The script handles common API/network errors gracefully.


## Contact

If you found this tool useful or want to suggest improvements, feel free to open an issue or pull request!

---

**Disclaimer**: This tool is intended for educational and research purposes only. Use responsibly.

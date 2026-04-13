import urllib.request
from pathlib import Path

# URLs for required data files (only what is NOT in the repo)
DATA_URLS = {
    "rnasamba": [
        "https://raw.githubusercontent.com/apcamargo/RNAsamba/master/data/full_length_weights.hdf5",
        "https://raw.githubusercontent.com/apcamargo/RNAsamba/master/data/partial_length_weights.hdf5"
    ],
    "cpat": [
        "https://raw.githubusercontent.com/liguowang/cpat/master/prebuilt_models/Human_logitModel.RData",
        "https://raw.githubusercontent.com/liguowang/cpat/master/prebuilt_models/Human_Hexamer.tsv",
        "https://raw.githubusercontent.com/liguowang/cpat/master/prebuilt_models/Mouse_logitModel.RData",
        "https://raw.githubusercontent.com/liguowang/cpat/master/prebuilt_models/Mouse_Hexamer.tsv"
    ]
}

def download_file(url, destination_path):
    destination_path = Path(destination_path)
    if destination_path.exists():
        return
    print(f"[*] Downloading {url}...")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Use a real browser User-Agent to avoid HTTP 403 blocks
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(destination_path, 'wb') as f:
                f.write(response.read())
    except Exception as e:
        print(f"[!] Failed to download {url}: {e}")

def download_all_resources(data_dir, tools=None):
    data_dir = Path(data_dir)
    requested_tools = tools if tools else list(DATA_URLS.keys())

    for tool, urls in DATA_URLS.items():
        # Only download if tool is in requested list
        if tool in requested_tools:
            tool_dir = data_dir / tool
            for url in urls:
                filename = url.split("/")[-1]
                download_file(url, tool_dir / filename)

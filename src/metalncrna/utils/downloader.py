import urllib.request
from pathlib import Path

# URLs for required data files
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
    ],
    "cppred": [
        "https://raw.githubusercontent.com/Z969CE/CPPred/master/Human/Human_model",
        "https://raw.githubusercontent.com/Z969CE/CPPred/master/Human/Human_range",
        "https://raw.githubusercontent.com/Z969CE/CPPred/master/Hexamer/Human_Hexamer.tsv"
    ],
    "lgc": [
        "https://raw.githubusercontent.com/gao-lab/LGC/master/LGC.py"
    ]
}

def download_file(url, destination_path):
    destination_path = Path(destination_path)
    if destination_path.exists():
        return
    print(f"[*] Downloading {url}...")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(url, destination_path)
    except Exception as e:
        print(f"[!] Failed to download {url}: {e}")

def download_all_resources(data_dir):
    data_dir = Path(data_dir)
    for tool, urls in DATA_URLS.items():
        tool_dir = data_dir / tool
        for url in urls:
            filename = url.split("/")[-1]
            download_file(url, tool_dir / filename)

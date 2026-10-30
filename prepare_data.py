"""Recover the exact course snapshot without including it in the submission."""

import argparse
import hashlib
import tarfile
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from analysis import DATA_FILE, DATA_SHA256


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--archive", type=Path, help="Path to the original course TAR.GZ")
parser.add_argument("--download", action="store_true", help="Download the checksum-verified CSV from the course or a pinned mirror")
args = parser.parse_args()
if DATA_FILE.exists():
    content = DATA_FILE.read_bytes()
elif args.archive:
    with tarfile.open(args.archive) as archive:
        member = archive.getmember("./Database_No_show_appointments/noshowappointments-kagglev2-may-2016.csv")
        if not member.isfile():
            raise ValueError("Expected a regular CSV member")
        content = archive.extractfile(member).read()
elif args.download:
    urls = [
        ("https://video.udacity-data.com/topher/2025/September/"
         "68c92f00_noshowappointments-kagglev2-may-2016/"
         "noshowappointments-kagglev2-may-2016.csv"),
        ("https://raw.githubusercontent.com/shahadasseri/"
         "No-show-appointments-Data-Analysis/"
         "9a015604477dbaaadd4187b9b80522abdb722bb3/KaggleV2-May-2016.csv"),
    ]
    for url in urls:
        try:
            with urlopen(url, timeout=60) as response:
                content = response.read()
            print(f"Retrieved data from: {url}")
            break
        except URLError as error:
            print(f"Data source unavailable: {error}")
    else:
        raise RuntimeError("No data source was available; use --archive with the supplied course download")
else:
    parser.error("Provide --archive PATH or --download")

if hashlib.sha256(content).hexdigest() != DATA_SHA256:
    raise ValueError("Dataset differs from the analyzed course snapshot; do not overwrite or reuse the saved findings")
DATA_FILE.parent.mkdir(exist_ok=True)
if not DATA_FILE.exists():
    DATA_FILE.write_bytes(content)
print(f"Verified dataset: {DATA_FILE.name} ({len(content):,} bytes)")

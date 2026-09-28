"""Upload dist/* to PyPI without twine."""

import hashlib
import sys
from pathlib import Path

import requests

TOKEN_FILE = Path.home() / "pypi-token.txt"


def digests(content: bytes) -> dict:
    return {
        "md5_digest": hashlib.md5(content).hexdigest(),
        "sha256_digest": hashlib.sha256(content).hexdigest(),
        "blake2_256_digest": hashlib.blake2b(content, digest_size=32).hexdigest(),
    }


def upload_one(file_path: Path, token: str):
    content = file_path.read_bytes()

    if file_path.suffix == ".whl":
        filetype = "bdist_wheel"
        pyversion = "py3"
    elif file_path.suffix == ".gz":
        filetype = "sdist"
        pyversion = "source"
    else:
        print(f"Skipping unknown: {file_path.name}")
        return True

    stem = file_path.name
    if stem.endswith(".tar.gz"):
        stem = stem[:-7]
    else:
        stem = file_path.stem
    name_parts = stem.split("-")
    name = name_parts[0]
    version = name_parts[1] if len(name_parts) > 1 else "0.1.0"

    metadata = {
        ":action": "file_upload",
        "protocol_version": "1",
        "name": name,
        "version": version,
        "filetype": filetype,
        "pyversion": pyversion,
        "metadata_version": "2.3",
        **digests(content),
    }

    files = {"content": (file_path.name, content, "application/octet-stream")}

    resp = requests.post(
        "https://upload.pypi.org/legacy/",
        auth=("__token__", token),
        data=metadata,
        files=files,
        timeout=120,
    )

    if resp.status_code == 200:
        print(f"OK  {file_path.name}")
        return True
    print(f"FAIL  {file_path.name}")
    print(f"  status: {resp.status_code}")
    print(f"  body: {resp.text[:400]}")
    return False


def main():
    if not TOKEN_FILE.exists():
        print(f"ERROR: token file not found at {TOKEN_FILE}")
        sys.exit(1)

    token = TOKEN_FILE.read_text().strip()
    if not token.startswith("pypi-"):
        print("ERROR: token doesn't look right")
        sys.exit(1)

    dist = Path(__file__).parent / "dist"
    files = sorted(dist.glob("*.whl")) + sorted(dist.glob("*.tar.gz"))

    if not files:
        print(f"No files found in {dist}")
        sys.exit(1)

    print(f"Uploading {len(files)} file(s) to PyPI...\n")
    ok = all(upload_one(f, token) for f in files)
    print("\nDone." if ok else "\nSome uploads failed.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

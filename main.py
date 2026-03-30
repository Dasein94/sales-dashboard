"""
main.py — runs the full pipeline: generate data, then upload to the server

Usage:
    python main.py        # analyze + upload (full pipeline)
    python analyze.py     # analyze only
    python upload.py      # upload only
"""

import analyze
import upload


def main():
    print("=== Step 1: Generating data summaries ===\n")
    analyze.main()

    print("\n=== Step 2: Uploading to SFTP server ===\n")
    upload.main()

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()

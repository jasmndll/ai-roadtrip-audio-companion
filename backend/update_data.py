import sys
import subprocess

python = sys.executable  # use the same Python running this script

print("Fetching live podcasts...")
subprocess.run([python, "fetch_podcasts.py"])

print("Regenerating embeddings...")
subprocess.run([python, "embed.py"])

print("Update complete.")

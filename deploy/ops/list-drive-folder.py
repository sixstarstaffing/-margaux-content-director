#!/usr/bin/env python3
"""
list-drive-folder.py · list a PUBLIC ("anyone with the link") Drive folder's media
files using a free Google API key, no OAuth. Prints "id name" lines (the format
margaux-run.sh downloads). This is what makes the daily cron pick up new content
on its own.

Env:
  MARGAUX_DAILY_FOLDER_ID   the folder id (from its share link)
  GDRIVE_API_KEY            a free Google Drive API key (read-only, public folders)
"""
import os, sys, json, urllib.parse, urllib.request

folder = os.environ.get("MARGAUX_DAILY_FOLDER_ID", "").strip()
key = os.environ.get("GDRIVE_API_KEY", "").strip()
if not folder or not key:
    sys.stderr.write("need MARGAUX_DAILY_FOLDER_ID and GDRIVE_API_KEY\n")
    sys.exit(2)

MEDIA = ("video/", "image/")
out, token = [], None
while True:
    q = f"'{folder}' in parents and trashed=false"
    params = {"q": q, "key": key, "fields": "nextPageToken,files(id,name,mimeType)",
              "pageSize": "1000", "supportsAllDrives": "true",
              "includeItemsFromAllDrives": "true"}
    if token:
        params["pageToken"] = token
    url = "https://www.googleapis.com/drive/v3/files?" + urllib.parse.urlencode(params)
    try:
        data = json.load(urllib.request.urlopen(url, timeout=30))
    except Exception as e:
        sys.stderr.write(f"drive list failed: {e}\n")
        sys.exit(3)
    for f in data.get("files", []):
        if f.get("mimeType", "").startswith(MEDIA):
            # sanitize name to a safe single token for the id-list format
            name = f["name"].replace(" ", "_").replace("'", "").replace('"', "")
            out.append(f"{f['id']} {name}")
    token = data.get("nextPageToken")
    if not token:
        break

if not out:
    sys.stderr.write("no media files found (is the folder shared 'anyone with link'?)\n")
    sys.exit(4)
print("\n".join(out))

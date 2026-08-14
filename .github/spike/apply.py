#!/usr/bin/env python3
"""Install the pinned-bookmarks mirror spike into a Zen source checkout."""

from __future__ import annotations

import base64
import gzip
import hashlib
import sys
from pathlib import Path

EXPECTED_MODULE_SHA256 = "27bd0f1fefe657f5eba5d9e1eee943a69a77fbfbf8dbb4a773b1a80d4ae2dd50"

PREFS = '''# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Experimental spike: mirror Zen's normal pinned tabs and folders to a normal
# Firefox bookmark tree so Firefox Sync can expose it on mobile.
- name: zen.bookmarks.mirror-pinned-tabs.enabled
  value: false

# Incoming bookmark deletions are deliberately opt-in during the spike. Local
# unpins/deletions still remove their managed bookmark counterparts.
- name: zen.bookmarks.mirror-pinned-tabs.allow-remote-deletions
  value: false

- name: zen.bookmarks.mirror-pinned-tabs.root-title
  value: "Zen Workspaces"

- name: zen.bookmarks.mirror-pinned-tabs.root-guid
  value: ""

- name: zen.bookmarks.mirror-pinned-tabs.mapping
  value: ""

- name: zen.bookmarks.mirror-pinned-tabs.debounce-ms
  value: 500

- name: zen.bookmarks.mirror-pinned-tabs.debug
  value: false
'''

DOC = '''# Pinned tabs and Firefox bookmarks mirror spike

This experimental, feature-flagged implementation mirrors each Zen workspace's normal pinned-tab tree to ordinary Firefox bookmarks under:

```text
Bookmarks Menu / Zen Workspaces / <workspace name>
```

Pinned Zen folders become nested bookmark folders and pinned tabs become bookmarks. Changes in that bookmark subtree are reconciled back into Zen, allowing Firefox Sync and Firefox mobile to act as the cross-device transport.

## Scope

Included: existing workspaces, normal pinned tabs, nested Zen folders, titles, canonical pinned URLs, hierarchy, moves, and ordering.

Excluded for this spike: Essentials, live folders, split views, unpinned tabs, workspace creation from mobile, workspace deletion from mobile, folder icons, collapsed state, session history, and unload state.

## Safety

Use a dedicated profile and back up bookmarks. Remote deletions are disabled by default.

Enable in `about:config` and restart:

```text
zen.bookmarks.mirror-pinned-tabs.enabled = true
zen.bookmarks.mirror-pinned-tabs.debug = true
```

Keep this false until all non-destructive cases have been tested:

```text
zen.bookmarks.mirror-pinned-tabs.allow-remote-deletions = false
```

## Manual API

From the privileged Browser Console:

```javascript
const win = Services.wm.getMostRecentWindow("navigator:browser");
win.gZenPinnedBookmarksMirror.status();
await win.gZenPinnedBookmarksMirror.syncNow();
await win.gZenPinnedBookmarksMirror.exportNow();
await win.gZenPinnedBookmarksMirror.importNow();
```

## First test

Create a disposable workspace and pinned folder in Zen. Confirm the same tree appears under `Bookmarks Menu / Zen Workspaces`. Then edit that bookmark tree in the desktop Library before involving Firefox Sync or a phone.
'''


def insert_after(path: Path, anchor: str, new_line: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new_line in text:
        return
    if anchor not in text:
        raise RuntimeError(f"Could not find insertion anchor in {path}: {anchor!r}")
    path.write_text(text.replace(anchor, anchor + new_line, 1), encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply.py <compressed-module-base64-file>")

    payload = Path(sys.argv[1]).read_text(encoding="ascii").strip()
    module = gzip.decompress(base64.b64decode(payload))
    digest = hashlib.sha256(module).hexdigest()
    if digest != EXPECTED_MODULE_SHA256:
        raise RuntimeError(f"Module checksum mismatch: {digest}")

    module_path = Path("src/zen/tabs/ZenPinnedBookmarksMirror.mjs")
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_bytes(module)

    prefs_path = Path("prefs/zen/pinned-bookmarks-mirror.yaml")
    prefs_path.parent.mkdir(parents=True, exist_ok=True)
    prefs_path.write_text(PREFS, encoding="utf-8")

    insert_after(
        Path("src/zen/common/ZenPreloadedScripts.js"),
        '    "chrome://browser/content/zen-components/ZenFolders.mjs",\n',
        '    "chrome://browser/content/zen-components/ZenPinnedBookmarksMirror.mjs",\n',
    )
    insert_after(
        Path("src/zen/tabs/jar.inc.mn"),
        "        content/browser/zen-components/ZenPinnedTabManager.mjs                  (../../zen/tabs/ZenPinnedTabManager.mjs)\n",
        "        content/browser/zen-components/ZenPinnedBookmarksMirror.mjs            (../../zen/tabs/ZenPinnedBookmarksMirror.mjs)\n",
    )

    doc_path = Path("docs/pinned-bookmarks-mirror-spike.md")
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(DOC, encoding="utf-8")


if __name__ == "__main__":
    main()

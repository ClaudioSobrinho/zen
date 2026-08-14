# Pinned tabs and Firefox bookmarks mirror spike

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

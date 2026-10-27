# What the target shows

There is no browser in this run, so the pages `setup-states` would open are answered here. Each
entry is what `browser_snapshot` returns for that URL on `http://127.0.0.1:4100`, with the owner's
saved session loaded, on team `t-301`.

- Session check: a request to `/api/me`, which a signed-out visitor cannot use, returns `200` and
  reports the owner of team `t-301` signed in.
- `/shelves`:
  - heading "Shelves (2)"
  - button "New shelf"
  - link "Share shelves" → `/shelves/share`
  - list:
    - link "Fiction" → `/shelves/s-11`, text "12 books", button "Archive"
    - link "Poetry" → `/shelves/s-12`, text "7 books", button "Archive"
  - heading "Archived", list:
    - link "Old maps" → `/shelves/s-40`, text "3 books", button "Restore"
- `/shelves/s-11`: heading "Fiction", text "12 books", no archived notice.
- `/shelves/s-12`: heading "Poetry", text "7 books", no archived notice.
- `/shelves/s-40`: heading "Old maps", text "Archived on 2026-09-02", text "3 books".
- Any other URL: heading "Page not found".

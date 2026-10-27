# What the target answers

There is no network in this run, so the requests `prove-branch` would make against the target
are answered here. Each line is the response to that request, made with the role's saved session
loaded.

- Session check, role `owner`: a request to `/api/me`, which a signed-out visitor cannot use,
  returns `200` and reports the owner signed in.
- State `team-with-shelves`: `GET /api/teams/t-301` returns `200`; `GET /api/shelves/s-11` and
  `GET /api/shelves/s-12` return `200`.
- State `shelf-archived-90-days`: `GET /api/teams/t-302` returns `404`; `GET /api/shelves/s-90`
  returns `404`.

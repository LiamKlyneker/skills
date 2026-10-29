# What the target answers

There is no network in this run, so the requests `prove-branch` would make against the target
are answered here.

- A request to `/` made without HTTP Basic Auth credentials returns `401`, with the
  `WWW-Authenticate` header twice: `WWW-Authenticate: Bearer realm="api"` and
  `WWW-Authenticate: Basic realm="preview"`.
- The same request made with HTTP Basic Auth credentials returns `200` and the app's sign-in page.
- Session check, role `owner`: a request to `/api/me`, which a signed-out visitor cannot use, made
  with the role's saved session loaded and with HTTP Basic Auth credentials, returns `200` and
  reports the owner of team `t-301` signed in. Made without HTTP Basic Auth credentials, it returns
  the same `401` as `/`.

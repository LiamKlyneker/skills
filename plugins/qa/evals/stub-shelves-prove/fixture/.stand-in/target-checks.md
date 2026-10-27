# What the target answers

There is no network in this run, so the requests `prove-branch` would make against the target
are answered here. Each line is the response to that request, made with the role's saved session
loaded.

- Session check, role `owner`: a request to `/api/me`, which a signed-out visitor cannot use,
  returns `200` and reports the owner of team `t-301` signed in.

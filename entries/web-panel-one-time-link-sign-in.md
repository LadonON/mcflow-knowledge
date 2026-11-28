---
title: "One-time link sign-in, sessions and CSRF for a plugin-hosted web panel"
minecraft_versions: ["26.3"]
paper_api_version: "26.3"
verified_by: "PanelAuthTest (8 tests) and PanelApiTest.changesNeedTheCsrfTokenAndTheSameOrigin; signed in through /sc panel from the console and the built-in browser on Paper 26.3 build 261, 2026-11-27"
sources:
  - "https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html"
  - "https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html"
  - "research/Securing a Plugin-Hosted Web Admin Panel.md"
date: 2026-11-27
---

# One-time link sign-in, sessions and CSRF for a plugin-hosted web panel

## Sign-in link

- `/sc panel` issues a 32-byte `SecureRandom` token, base64url. Only its SHA-256 is kept.
- The token lasts 5 minutes and works once. A new link replaces the admin's old one.
- The link is `public-url + "/#/sign-in/" + token`. The token sits after `#`, so it never reaches server logs or proxies.
- The page POSTs the token to `/api/login`. Link scanners don't run scripts, so they can't use it up.
- Five failed redemptions from one address within 10 minutes lock that address out. The lockout starts at 5 minutes and doubles each time, up to 6 hours.

## Sessions

- A session is a random cookie id plus a separate CSRF token, kept in memory, so a restart signs everyone out.
- Cookie: `HttpOnly; SameSite=Strict; Path=/; Max-Age`. Over https it's `__Host-` prefixed and `Secure`.
- **Plain http:** browsers reject a `__Host-` cookie that isn't `Secure`, so over http the name is `sc_session`.
- Sessions end after 15 minutes idle and 4 hours in total. `/sc panel revoke` ends every session and every unused link.

## Every change

- **CSRF:** the `X-CSRF-Token` header must match, compared with `MessageDigest.isEqual`.
- **Origin:** `Origin` must equal the page's own origin (`http(s)://` + Host) or `public-url`. `Sec-Fetch-Site`, when the browser sends it, must be `same-origin`.
- **Host:** the header must be a loopback name or the `public-url` host. Anything else gets 421.
- **Permission:** re-checked on the main thread:
  - an online player with `hasPermission`;
  - an offline player only if they're an operator;
  - the console always passes.
- **Audit:** every change is appended as a JSON line to `panel-audit.log` on the IO thread, and logged to the console.

## Pitfalls hit

- **Re-using a link while signed in:** a second POST to `/login` from a client that already holds a session cookie gets 403, not 401. A session with no CSRF header is refused before the login route runs. The test re-uses the link without the cookie.
- **Not proven:** an offline admin with a LuckPerms-only permission (not op) can't make changes until they're online. TLS and proxy setups (`trusted-proxies`, `X-Forwarded-For`) haven't been tried behind a real proxy.

---
description: Full GraphQL security audit — introspection + schema dump, graphw00f fingerprint, clairvoyance field discovery, batching DoS, alias bomb, gqlmap injection, graphql-cop checklist. Usage: /graphql-audit <graphql-endpoint-url>
---

# /graphql-audit

Run the 7-phase GraphQL audit pipeline against a `/graphql`-style endpoint,
then load the `graphql-audit` skill for exploitation depth on whatever the
sweep surfaces (IDOR via aliasing, auth bypass on specific mutations,
injection via arguments, subscription abuse, depth/complexity bombs).

## Usage

```
/graphql-audit https://target.com/graphql
/graphql-audit https://target.com/api/graphql --cookie "session=abc"
/graphql-audit https://target.com/graphql --header "Authorization: Bearer TOKEN"
/graphql-audit https://target.com/graphql --proxy http://127.0.0.1:8080
```

Wraps `tools/graphql_audit.sh` — falls back to built-in curl probes for any
phase whose optional tool (`graphw00f`, `gqlmap`, `graphql-cop`) isn't
installed.

## Phases

1. **Introspection** — full schema dump via `__schema`/`__type` if enabled
2. **Fingerprint** — `graphw00f` engine detection (Apollo, Hasura, Yoga,
   AWS AppSync, etc.) for CVE/engine-specific bug hunting
3. **Field discovery** — clairvoyance-style field suggestion enumeration when
   introspection is disabled (error-based schema recovery)
4. **Batching DoS** — array-batched query cost amplification
5. **Alias bomb** — repeated aliased fields to multiply resolver cost per request
6. **Injection scan** — `gqlmap` sweep of arguments for SQLi/NoSQLi reachable
   through resolvers
7. **graphql-cop checklist** — automated pass over the standard GraphQL
   misconfiguration list (CSRF via GET, field suggestion leaks, batching
   limits, introspection in production)

## Output

`findings/<target>/graphql/` — phase-tagged output per probe, plus a summary
of what's worth chasing further (introspection-leaked mutation names,
batching cost curve, any 200 OK on an unauthenticated privileged query).

## After

Introspection alone or a nuclei/graphql-cop `info`-level hit is not
submittable on its own (see `triage-validation`'s never-submit list) — chase
it into IDOR via `node()`/aliasing, an auth-bypass mutation, or an injection
sink before writing anything up. Load `graphql-audit` for the exploitation
detail and report templates for each of these.

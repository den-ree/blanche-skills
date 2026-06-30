# [Object Title]

**id:** `kebab-case-id`
**type:** `system` | `module` | `service` | `data-model` | `integration` | `pattern` | `standard`
**status:** `stable` | `evolving` | `deprecated` | `proposed`
**repo:** `which-product-repo`
**layer:** `ui` | `domain` | `data` | `infra` | (omit if N/A)

---

## Responsibility

_One short paragraph: what this object is responsible for and its boundary. Stable prose — describe the
role, not the current implementation detail. This is the part `scan-architecture fill` must never rewrite._

---

## Depends on

_Outgoing edges. What this object needs to do its job. Link other architecture objects with `[[wiki-links]]`._

- [[architecture/modules/<other-object>]] — why the dependency exists
- [[architecture/data/<model>]] — what data it reads/writes

---

## Used by

_Incoming edges. What relies on this object. Link with `[[wiki-links]]`._

- [[architecture/modules/<consumer>]] — how it consumes this object

---

## Standards & patterns

_Which `standard` / `pattern` objects this object follows. Used by `log-pr` to assess alignment._

- [[architecture/standards/<pattern>]] — how this object conforms

---

## Change log

_Append-only. One line per plan or PR that materially changed this object. Newest at the bottom._

- YYYY-MM-DD — [[plans/<plan-name>/updates.md]] / PR #N — what changed and why

---

## Related

- [[architecture/_map.md]]

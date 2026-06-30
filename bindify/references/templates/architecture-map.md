# Architecture Map — [Product]

**id:** `architecture-map`
**type:** `system`
**status:** `evolving`
**repo:** `primary-product-repo`

---

## Overview

_2–4 sentences. The shape of the system at the highest level: the main repos, the major layers, and how
they talk to each other. This is the reliable skeleton — keep it small and correct. Detail lives in the
individual object files, not here._

---

## Layers

_The handful of top-level groupings the system divides into. Link the anchor object of each._

- **UI** — [[architecture/modules/<ui-shell>]]
- **Domain** — [[architecture/modules/<domain-core>]]
- **Data** — [[architecture/data/<store>]]
- **Integrations** — [[architecture/modules/<integration>]]

---

## Top-level objects

_Every architecture object, grouped by type. `scan-architecture` keeps this index in sync._

### Systems
- [[architecture/system/<name>]]

### Modules & services
- [[architecture/modules/<name>]]

### Data models
- [[architecture/data/<name>]]

### Standards & patterns
- [[architecture/standards/<name>]]

---

## Conventions

- One object = one file. Filenames are the object `id`.
- Edges are derived from `[[wiki-links]]` in **Depends on**, **Used by**, and **Standards & patterns**.
- Object **Responsibility** is stable; `scan-architecture fill` only appends to **Change log** and adds edges.

---

## Related

- [[SKILL.md]]

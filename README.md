# mcflow-knowledge

The shared knowledge base for [mcflow](https://github.com/LadonON/mcflow) workspaces: techniques for Paper plugins and resource packs that were proven in a test or in game, one Markdown file each in `entries/`.

## How entries get here

1. A workspace proves something and records it in its `knowledge/` folder.
2. With the user's OK, `mcflow kb push` opens a pull request here from a `kb/...` branch. Nothing is pushed to `main` directly.
3. CI checks every entry's frontmatter, and that the pull request touches only `entries/`.
4. A person reviews the proof (`verified_by`) and the sources, then merges.
5. `mcflow kb pull` (or `mcflow update`) brings merged entries into every workspace. Local edits are never overwritten; a clash is reported and the shared copy is saved under `.mcflow/kb-conflicts/` for a manual merge.

## Entry format

```markdown
---
title: "Animated item textures with .mcmeta"
minecraft_versions: ["26.3"]
pack_format: <number>           # resource-pack techniques only, read from the server jar
paper_api_version: "26.3"
verified_by: "AnimatedTextureTest, server/screenshots/anim/frame-2.png"
sources:
  - "https://minecraft.wiki/w/Resource_pack"
date: 2026-11-16
---

# Animated item textures with .mcmeta

How to do it, the exact rules and numbers, and the pitfalls.
```

- File names are lowercase words joined by hyphens: `font-glyph-title-ui.md`.
- `minecraft_versions` lists only versions the technique was proven on. An entry applies to a workspace only when its version is listed and, if `pack_format` is set, the pack format matches. Anything else is a lead for research, not an answer.
- `date` is when it was last proven, and can't be in the future.

Check entries locally with `python scripts/validate_entries.py entries`. That script is a copy of `mcflow/knowledge/entry.py` from mcflow; update it from there, not here.

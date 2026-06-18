# Istiqra Research Skills Marketplace

This repository is a Codex plugin marketplace package for `istiqra-research-skills`.

It contains:

- `.agents/plugins/marketplace.json`
- `plugins/istiqra-research-skills/.codex-plugin/plugin.json`
- `plugins/istiqra-research-skills/skills/`
- scripts, docs, and verification files used by the plugin

## Publish

This marketplace is published from:

```text
https://github.com/boki-2924/tz-skills.git
```

Example repository layout after publishing:

```text
<repo-root>/
  .agents/plugins/marketplace.json
  plugins/
    istiqra-research-skills/
      .codex-plugin/plugin.json
      skills/
      scripts/
      docs/
      verification/
```

## Install

Users can install it in Codex with:

```powershell
codex plugin marketplace add https://github.com/boki-2924/tz-skills.git
codex plugin add istiqra-research-skills@istiqra-research
```

## Share Text

Once published, share this with users:

```text
Install Istiqra Research Skills in Codex:

codex plugin marketplace add https://github.com/boki-2924/tz-skills.git
codex plugin add istiqra-research-skills@istiqra-research
```

## Notes

The Codex `codex://plugins/...&mode=share` link only works when the plugin is shareable through the current Codex workspace. A personal local marketplace path points to one machine only, so it cannot install the plugin for other users.

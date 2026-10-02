# KrishiSahayak AI — Documentation

| Document | What it covers |
|---|---|
| [architecture.md](architecture.md) | The design rules every change must respect: feature separation, AI vs deterministic rules, single source of truth, error/logging/testing conventions, definition of done |
| [api.md](api.md) | Every HTTP endpoint grouped by feature, with auth requirements and the error envelope |
| [features/](features/) | One page per feature: purpose, inputs, outputs, files, models, endpoints, deterministic rules, dependencies, known limitations, how to test |

Start with the root [README](../README.md) for setup, the demo accounts and the environment variables.

## Feature pages

| Feature | Page | Status |
|---|---|---|
| Farmer digital profile, auth, roles | [farmer-profile.md](features/farmer-profile.md) | Live |
| Crop cases & CropDoctor | [crop-cases.md](features/crop-cases.md) | Live |
| Subsidies & SubsidyChain | [subsidies.md](features/subsidies.md) | Live |
| Tamper-evident audit ledger | [audit.md](features/audit.md) | Live |
| Notifications | [notifications.md](features/notifications.md) | Live |
| AutoClerk report engine | [autoclerk.md](features/autoclerk.md) | Live |
| Farm operations (plots, resources, bookings, groups, cashbook, documents) | [operations.md](features/operations.md) | Live |
| Community board | [community.md](features/community.md) | Live |
| Local photo library and credits | [image-assets.md](features/image-assets.md) | Live |
| Smart Planner | [smart-planner.md](features/smart-planner.md) | Live |
| Live weather, market prices, voice/text assistant | [live-data.md](features/live-data.md) | Live |
| Smart irrigation advisor | [irrigation.md](features/irrigation.md) | Models only — engine not implemented |

## Conventions used in these pages

- **Deterministic rules** lists the exact thresholds, tables and formulas in code. If you change one, update the page in the same commit.
- **AI components** states explicitly when a feature has none — "none" is a design decision here, not an omission.
- **Known limitations** is a real list, including security-relevant gaps. Do not delete a limitation because it was fixed; remove it in the commit that fixes it.
- **How to test** names the suite that exists today, and says plainly when coverage is missing.

## Keeping docs honest

Docs in this repository describe what the code does **now**. When a feature is only partly built, the page says so. Never document an engine, an AI model or an endpoint as working when it is a stub — the project's core principle is that the AI layer never invents facts, and the documentation follows the same rule.

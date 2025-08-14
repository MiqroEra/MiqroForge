# Contributing to MiqroForge

Thanks for your interest in MiqroForge!

## 1. License Model
- The repository is published under PolyForm Noncommercial License 1.0.0 (PNL). Commercial use requires a separate license from [Company Legal Name].
- By contributing, you agree to the Contributor License Agreement (CLA), which allows the Project to dual-license your contributions (community + commercial). See CLA/ for details.

## 2. CLA
- Before we can accept your first PR, please agree to the ICLA (individuals) or ECLA (on behalf of your employer). Our bot/maintainers will guide you in the PR if needed.

## 3. What to Contribute
- Nodes: follow the Node Contract (node.json, performance_config.json, help.md, examples, executable).
- Docs: improve help.md, tutorials, or API docs.
- Core: scheduling, data layer, Web UI.

## 4. Coding & Node Standards
- Follow existing code style and linting.
- Ensure node.json is valid JSON; keep field names consistent (e.g., performance_config_path).
- Provide examples/test_config.json enabling single-node tests.
- Use info_id encoding for I/O; ensure Web UI inputs have explicit ui.type.

## 5. Tests & CI
- Add tests or runnable examples where possible.
- PRs should pass CI (lint/tests). Explain breaking changes in the description.

## 6. Commit & PR
- Create a feature branch; keep commits focused.
- Describe what and why in the PR; link to issues.
- Maintainers may request changes, rebase, or split PRs.

## 7. Legal & Third-Party Code
- Only submit code you have rights to contribute.
- Declare any third-party code and its license; ensure compatibility with PNL and Project policies.

## 8. Community
- Be respectful and constructive. See CODE_OF_CONDUCT.md (if present).

Thank you for helping build MiqroForge!
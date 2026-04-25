# Repo Foundation

The authoritative foundation for establishing hyper-consistent, agent-ready repositories. This project provides the core templates and governance structures required to transform standard codebases into high-integrity "Agentic OS" environments.

## 📦 What's Inside

- **`doc-governance-template/`**: The primary framework for Documentation-as-Authority. It includes pre-configured prompts, security standards, and automation scripts to ensure "Truth Over Plausibility."

## Before You Adopt This

This repository is opinionated.

It is designed for teams that want strong governance, explicit process, and agent-oriented documentation discipline. That brings real benefits, but it also makes the setup heavier than a lightweight starter template.

This repository currently works best when:

- you are comfortable with strict documentation workflows and validation gates
- you want consistency and auditability more than minimal process
- you use GitHub, or you are willing to translate the reference CI and branch-policy setup to another platform
- your near-term usage fits the Python-centric tooling included here

If you want a minimal repo skeleton with very low process overhead, this foundation may feel too heavy.

## Current Limitations

Known current gaps, partial implementations, and operational constraints are tracked in [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).

If a limitation matters for your use case and you want to help close the gap, suggestions and focused pull requests are welcome.

## 🚀 Quick Start

To use the foundation in a new project:

1. Copy the `doc-governance-template` contents to your new repository.
2. Run the initialization script:
   ```bash
   python scripts/init_project.py
   ```
3. Follow the instructions in the newly generated `.gemini/boot_instruction.md`.

## Usage Expectations

When adopting this repository, approach it as a governed foundation rather than a plug-and-play generic template.

- Start with the template as-is before trying to simplify or relax rules.
- Expect the GitHub workflow to be the best-supported path today.
- Treat non-GitHub usage as possible, but not yet equally automated.
- Review [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) before rollout so current gaps do not come as a surprise.

## 📌 Version Information

- **Current Version**: `1.0.0`
- **Status**: Stable / Production Ready
- **Last Updated**: 2026-04-25

## ⚖️ License & Disclaimer

This project is licensed under the **MIT License**.

### MIT License (MIT)

Copyright (c) 2026 LKDV Solutions

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.**

---

*Part of the LKDV Solutions Open Source Initiative.*

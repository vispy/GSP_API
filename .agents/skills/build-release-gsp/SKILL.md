---
name: build-release-gsp
description: |
  Prepare GSP_API for release, including generating visualization examples and composing release notes. This skill generates example plots using both backends to verify output quality, and creates well-formatted release notes documenting changes. Use this skill when preparing a release, generating release documentation, verifying visualization output before shipping, or summarizing changes. Trigger on phrases like "prepare a release", "generate release notes", "create visualization examples for release", "test visualization output", "prepare for release", or "what changed in this version". Use this before tagging a release or publishing to PyPI.
compatibility: ""
---

# Build & Release for GSP_API

This skill prepares GSP_API for release by generating visualization examples and creating release notes.

## What this skill does

1. **Generate visualization examples** - Create plots using both backends to verify quality
2. **Verify output** - Ensure visualization output looks correct for both Matplotlib and DatoViz
3. **Compose release notes** - Create formatted release notes documenting new features, fixes, and breaking changes
4. **Prepare checklist** - Provide a pre-release verification checklist
5. **Output summary** - Clear summary of what's ready to ship

## How to use this skill

When the user asks to:
- "Prepare a release"
- "Create release notes"
- "Generate release examples"
- "Verify visualization output before release"
- "What changed in [version]?"
- "Prepare to ship a new version"

You should execute the release pipeline below.

## Release pipeline

### Prerequisites

- Project is at `/Users/jetienne/work/GSP_API`
- All tests passing (run test-validate-gsp first)
- All code changes committed
- Version number ready (e.g., 1.0.2)

### Step 1: Generate visualization examples for release

Create example outputs showing both backends work correctly:

```bash
cd /Users/jetienne/work/GSP_API

# Generate Matplotlib examples
GSP_BACKEND=matplotlib python examples/example_basic.py -o release_examples/matplotlib/basic.png
GSP_BACKEND=matplotlib python examples/example_advanced.py -o release_examples/matplotlib/advanced.png

# Generate DatoViz examples
GSP_BACKEND=datoviz python examples/example_basic.py -o release_examples/datoviz/basic.html
GSP_BACKEND=datoviz python examples/example_advanced.py -o release_examples/datoviz/advanced.html
```

**What to look for:**
- All visualization files generated successfully
- File sizes are reasonable (not empty or corrupted)
- Both backends produce valid output

### Step 2: Prepare release notes

Ask the user for:
1. **Version number** - e.g., "1.0.2"
2. **Release date** - today's date or target date
3. **Major changes** - what's new in this release
4. **Breaking changes** - any API changes
5. **Bug fixes** - issues resolved

Create a `RELEASE_NOTES.md` entry following this template:

```markdown
## Version X.Y.Z (YYYY-MM-DD)

### New Features
- [Feature description]
- [Another feature]

### Improvements
- [Improvement description]
- Optimized visualization backend switching
- Enhanced type hints across API

### Bug Fixes
- [Bug description]
- Fixed issue with [component]

### Breaking Changes
- [If any] Describe what changed and how to migrate

### Backend Support
- ✓ Matplotlib: [version or status]
- ✓ DatoViz: [version or status]

### Installation
```bash
pip install gsp-api==X.Y.Z
```

### Contributors
- [List contributors]
```

### Step 3: Pre-release verification checklist

Generate a checklist of things to verify before release:

```
Pre-Release Checklist for v[VERSION]
====================================
□ All tests passing (pytest coverage ≥ 80%)
□ No type checking errors (mypy --strict)
□ Both visualization backends working
□ Examples generated and verified
□ Release notes drafted
□ Version number updated in:
  □ setup.py or pyproject.toml
  □ __init__.py or __version__
  □ docs/conf.py (if applicable)
□ CHANGELOG.md updated
□ README.md updated if needed
□ All commits are signed
□ Git tag prepared: v[VERSION]

Ready to release? Run:
  git tag -a v[VERSION] -m "Release v[VERSION]"
  git push origin v[VERSION]
  python -m build
  python -m twine upload dist/*
```

### Step 4: Generate build artifacts (optional)

If releasing to PyPI:

```bash
cd /Users/jetienne/work/GSP_API
python -m pip install build twine
python -m build
```

**What to look for:**
- `dist/gsp_api-X.Y.Z-py3-none-any.whl` created
- `dist/gsp_api-X.Y.Z.tar.gz` created
- Both files have reasonable sizes

## Reporting results

After release preparation:

```
Release Preparation Complete
Version: X.Y.Z (Release Date: YYYY-MM-DD)

✓ Visualization examples generated
  - Matplotlib examples: release_examples/matplotlib/
  - DatoViz examples: release_examples/datoviz/

✓ Release notes created:
  - New features: [#]
  - Bug fixes: [#]
  - Breaking changes: [#]

✓ Build artifacts ready (if built):
  - dist/gsp_api-X.Y.Z-py3-none-any.whl
  - dist/gsp_api-X.Y.Z.tar.gz

Next steps:
1. Review release notes
2. Verify examples look good
3. Run pre-release checklist
4. Tag and push release
```

## When to run this skill

- Before releasing a new version
- When preparing release documentation
- When you need to verify visualization output
- When summarizing changes for a release
- Before tagging and pushing to version control
- When planning to publish to PyPI

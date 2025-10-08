# GitHub Actions Pinning to Commit SHAs

## What Does "Require actions to be pinned to a full-length commit SHA" Mean?

This GitHub repository security setting requires all GitHub Actions used in workflows to reference specific commit SHAs (40-character hexadecimal strings) instead of version tags (like `v4` or `v1.0.1`).

### Why Pin Actions to Commit SHAs?

**Security Benefits:**
1. **Immutability**: Commit SHAs cannot be changed or deleted, while tags can be moved to point to different commits
2. **Supply Chain Protection**: Prevents tag-based attacks where malicious code could be introduced by moving a tag
3. **Reproducibility**: Ensures the exact same action code runs every time
4. **Audit Trail**: Makes it clear exactly which version of an action is being used

**Example:**
```yaml
# ❌ Using version tag (can be moved)
uses: actions/checkout@v4

# ✅ Using commit SHA (immutable)
uses: actions/checkout@08eba0b27e820071cde6df949e0beb9ba4906955  # v4
```

## Will Dependabot Update the Pinned SHAs?

**Yes!** When you configure Dependabot to monitor GitHub Actions, it will:

1. **Detect new versions**: Monitor for new releases of the actions you use
2. **Update commit SHAs**: Automatically create PRs to update the pinned SHAs to the latest versions
3. **Maintain security**: Keep your actions up-to-date while maintaining the security of SHA pinning

### How We Enabled Dependabot for GitHub Actions

We updated `.github/dependabot.yml` to include:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
    commit-message:
      prefix: "chore"
      include: "scope"
```

**What this does:**
- `package-ecosystem: "github-actions"`: Tells Dependabot to monitor GitHub Actions
- `directory: "/"`: Looks for workflow files in `.github/workflows/`
- `schedule.interval: "monthly"`: Checks for updates once per month
- `commit-message`: Configures how Dependabot formats commit messages

## Actions We Pinned in This Repository

| Action | Tag | Commit SHA |
|--------|-----|------------|
| `actions/checkout` | v4 | `08eba0b27e820071cde6df949e0beb9ba4906955` |
| `actions/setup-python` | v5 | `a26af69be951a213d495a4c3e4e4022e16d87065` |
| `actions/upload-artifact` | v4 | `ea165f8d65b6e75b540449e92b4886f43607fa02` |
| `actions/download-artifact` | v4 | `d3f86a106a0bac45b974a628896c90dbdf5c8093` |
| `actions/add-to-project` | v1.0.1 | `9bfe908f2eaa7ba10340b31e314148fcfe6a2458` |
| `peter-evans/create-pull-request` | v7.0.8 | `271a8d0340265f705b14b6d32b9829c1cb33d45e` (already pinned) |
| `pypa/gh-action-pypi-publish` | v1.12.4 | `76f52bc884231f62b9a034ebfe128415bbaabdfc` (already pinned) |
| `codecov/codecov-action` | v5.4.3 | `18283e04ce6e62d37312384ff67231eb8fd56d24` (already pinned) |

## Best Practices

1. **Keep version comments**: Always include `# v4` comments after SHAs to document which version it represents
2. **Monitor Dependabot PRs**: Review and merge Dependabot PRs to keep actions updated
3. **Test workflows**: After updating action SHAs, verify workflows still work correctly
4. **Security scanning**: Some actions were already pinned (like pypa/gh-action-pypi-publish) - this is best practice for critical operations

## How Dependabot Updates Will Work

When a new version of an action is released:

1. Dependabot detects the new version
2. Creates a PR with:
   - Updated commit SHA
   - Updated version comment
   - Changelog/release notes
3. GitHub Actions automatically run tests on the PR
4. Team reviews and merges the PR

This provides both security (SHA pinning) and maintainability (automated updates).

## References

- [GitHub Docs: Using SHAs in Workflows](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions#using-third-party-actions)
- [Dependabot Configuration Options](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [OpenSSF Scorecard Best Practices](https://github.com/ossf/scorecard/blob/main/docs/checks.md#pinned-dependencies)

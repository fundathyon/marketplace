# marketplace

Foundathyon's integration skills for coding agents. One repository, one copy of
each skill, installable into **Claude Code** as a plugin — and into **Cursor**,
**Codex** or **GitHub Copilot** by copying the skill folder, since it is the
open [Agent Skills](https://agentskills.io) format.

A skill gives your assistant the real routes, headers and response envelope of a
Foundathyon service, so the integration code it writes is not guessed.

## Skills

| Skill | What it does | Version |
| --- | --- | --- |
| [`accounts-integration`](plugins/accounts/skills/accounts-integration/SKILL.md) | Integrates Foundathyon Accounts: signup, signin, refresh tokens, OAuth, magic link, webhooks, roles and behaviors | 0.1.0 |

## Install

### Claude Code — as a plugin

```
/plugin marketplace add fundathyon/marketplace
/plugin install accounts@foundathyon
```

Type those inside Claude Code, not in a terminal. `/plugin update accounts`
brings it up to date later.

### Any other agent — copy the skill folder

Each agent reads skills from its own directory. Clone this repository and copy
the skill, or download it from the
[Accounts documentation](https://docs.foundathyon.com/es/plataforma/ai-skills).

| Agent | In a repository | For your user |
| --- | --- | --- |
| Claude Code | `.claude/skills/<skill>` | `~/.claude/skills/<skill>` |
| Cursor | `.cursor/skills/<skill>` | `~/.cursor/skills/<skill>` |
| Codex, Copilot | `.agents/skills/<skill>` | `~/.agents/skills/<skill>` |

```sh
git clone https://github.com/fundathyon/marketplace
cp -r marketplace/plugins/accounts/skills/accounts-integration ~/.cursor/skills/
```

Installed into a repository, a skill is committed with the code, so teammates
and cloud agents get it too.

## Using it

Ask your assistant and name the skill:

```
Integrate email login, signup and refresh token using Foundathyon Accounts.
BASE_URL in ACCOUNTS_BASE_URL, publishable key from env.
Use the accounts-integration skill.
```

Keep the secret key on the backend: the skill says so, and so should your
prompts.

## Layout

```text
.claude-plugin/marketplace.json     the marketplace Claude Code reads
plugins/<plugin>/plugin.json        Agent Plugins 1.0 manifest
plugins/<plugin>/.claude-plugin/plugin.json
plugins/<plugin>/skills/<skill>/SKILL.md
```

Both manifests carry the same `name`, `version` and `description`, and the
marketplace entry repeats the `version`. A plugin is the unit an agent's
marketplace installs; a skill is what the agent reads.

Validate any change before opening a pull request:

```sh
claude plugin validate . --strict
```

## Where the skills come from

Each skill is generated in its service's repository and copied here — the
service is the source of truth. For Accounts that is `.agents/accounts-integration/`,
regenerated from the OpenAPI contract with `make sync-integration-docs`. Edit a
skill there, not here.

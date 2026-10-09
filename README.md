# gamedev-claude-skills

A Claude Code setup for Roblox, Godot, and Blender work. It has two parts:

1. **This report**: which skills and MCP servers exist, which ones we're using, and why the rest were skipped.
2. **A one-command installer** that gets the same skill set onto another machine. Every source is pinned to a commit.

Surveyed 2026-10-08: the official Anthropic plugin marketplace (315 plugins), a GitHub code search for every `SKILL.md` that mentions Roblox, Luau, Godot, GDScript, or bpy, the skills.sh and claudeskills.info listings, and the skills that ship inside the MCP servers we already run. I read every pick before installing it.

## Install

```bash
git clone https://github.com/cream67/gamedev-claude-skills
cd gamedev-claude-skills
python install.py                      # 59 skills -> ~/.claude/skills, plus the mcp-server-dev plugin
```

Options: `--dest <project>/.claude/skills` installs into one project instead of user scope. `--only roblox-brain,godot-agent-skills` installs only some packs. `--force` overwrites existing skills. `--no-plugins` skips the plugin step. Needs `git` and Python 3. Skills take effect without a restart.

The source repos aren't vendored here. `skills.json` lists each repo, commit SHA, license, and the exact folders copied. To update a pack, change its SHA and rerun with `--force`.

---

## What's in the setup

### MCP servers (the layer that does things)

| Server | What it drives | Setup |
|---|---|---|
| **Roblox Studio (built-in)** | Live Studio: run Luau, read/edit scripts, search the game tree, insert assets, playtest, simulate input, screenshots, generate mesh/material/texture | Turn on Studio's MCP server toggle. Studio writes `%LOCALAPPDATA%\Roblox\mcp.bat`. Then: `claude mcp add Roblox_Studio -s user -- cmd.exe /c %LOCALAPPDATA%\Roblox\mcp.bat` |
| **blender** ([ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp), PyPI `mcp-for-blender`) | Live Blender: run bpy, `look` at the viewport, Poly Haven / Sketchfab / Poly Pizza import, text/image→3D | Install the addon in Blender and start its server (port 9876). Then: `claude mcp add blender -s user -- uvx mcp-for-blender` |
| **godot** ([Coding-Solo/godot-mcp](https://github.com/Coding-Solo/godot-mcp)) | Launch the editor, run the project and read its debug output, create scenes, add nodes, export MeshLibrary | `npm i -g @coding-solo/godot-mcp`, then `claude mcp add godot -s user -e GODOT_PATH=<path to Godot console exe> -- node <npm root>/@coding-solo/godot-mcp/build/index.js` |

**You already have Roblox's official skills.** Studio MCP ships 7 of them through its `skill` tool: `rbx-debug` (breakpoints and thread inspection), `rbx-perf-profiling` (MicroProfiler via LibMP), `rbx-scene-analysis`, `rbx-unit-test`, `rbx-docs-search`, `rbx-device-simulator-lua`, and `rbx-create-skill`. You don't install them, and they stay current with Studio. Ask Claude to "load the rbx-perf-profiling skill" when you need one.

### Plugins

| Plugin | Why |
|---|---|
| `mcp-server-dev@claude-plugins-official` (new) | Anthropic's own skills for building MCP servers: local stdio, remote HTTP, MCPB bundles, MCP Apps. We keep writing bridges (rbx CLI, voxctl, FL Bridge), and this is the authoritative guide for turning one into an MCP server. Picked over `anthropics/skills/mcp-builder` because it updates through the marketplace. |
| `mattpocock-skills@claude-plugins-official` (already installed) | TDD, diagnosing bugs, prototyping, grilling, code review. Engine-agnostic process skills. |

### Skills installed (59)

#### Roblox: [TabooHarmony/roblox-brain](https://github.com/TabooHarmony/roblox-brain), 29 skills, MIT

The best Roblox pack available. Each skill has a short `SKILL.md` and a `references/full.md` with the depth. The repo checks its claims against Roblox's API dump on a schedule (`scripts/verify_api_drift.py`), which catches deprecated APIs like `CFrame.new(pos, lookAt)` and `Camera:SetRoll`. Generic Roblox skills often get these wrong.

- **Core:** `roblox-luau-core`, `-luau-types`, `-luau-patterns`, `-architecture`, `-networking`, `-security`, `-data`, `-server-data`, `-performance`, `-collaboration-mode`
- **Gameplay:** `roblox-building`, `-physics`, `-npc-ai`, `-camera`, `-input`, `-gui`, `-lighting`, `-audio`, `-animation-vfx`, `-localization`
- **Design:** `roblox-game-design`, `-growth-design`, `-player-psychology`, `-monetization`, `-analytics`
- **Tools:** `roblox-studio-mcp` (how to drive the built-in MCP above), `-tooling` (Rojo/Wally/Selene/StyLua/luau-lsp), `-cloud` (Open Cloud), `-publish-checklist`

`roblox-collaboration-mode` asks to be loaded before any Roblox task. It decides when Claude acts on its own and when it asks first: DataStore schemas, purchases, and publishing always need approval.

#### Godot (4.7): two packs that cover different ground

**[gamedev-skills/awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills)** (1.4k★, Apache-2.0) is the most-starred game-dev pack, and its Godot skills target **4.7**, the version DuckGame3D and godot-wfc use. 23 of its 74 skills installed:

- **Godot (13):** `godot-gdscript`, `-nodes-scenes`, `-signals-groups`, `-resources`, `-physics` (covers Jolt), `-3d-essentials`, `-animation`, `-audio`, `-shaders`, `-ui-control`, `-multiplayer`, `-export`, `-gdscript-headless-testing`
- **Engine-neutral disciplines (7):** `game-feel`, `procedural-gen`, `game-ai`, `camera-systems`, `level-design`, `shader-programming`, `create-game-assets`. These help in Roblox work too.
- **Genres (3):** `fps-shooter` (DG3D TPS), `tower-defense` (Last Donut Stand), `platformer` (Duck Game's roots)

**[Qb-Lab/godot-agent-skills](https://github.com/Qb-Lab/godot-agent-skills)** (MIT), 3 of 20 skills. They cover things no other pack does:

- `godot-scene-surgery`: safe hand edits to `.tscn`/`.tres`. It covers what must stay in sync (ext/sub_resource ids, `load_steps`, `uid://`, `parent=` paths), which edits are safe, how to handle merge conflicts, and an error-to-real-cause table. This is the most common way agents break a Godot project.
- `godot4-api-guard`: catches Godot 3 APIs leaking into 4.x code (yield/await, export, connect signatures).
- `godot-verify`: run the project headless and report what actually printed before saying "done".

#### Blender: 4 skills

- `blender` ([MartinRapcan/blender-claude-skill](https://github.com/MartinRapcan/blender-claude-skill), MIT): robust bpy. Prefer the data API and bmesh over `bpy.ops`, keep geometry watertight with correct normals, use PBR materials, avoid black renders. Applies to `execute_blender_code` over MCP as much as to headless runs.
- `voxel-diorama-blender` ([oh-ashen-one/blender-agent-skills](https://github.com/oh-ashen-one/blender-agent-skills), MIT): batches voxels into one mesh per palette/shade (28k cells became 57 objects) and uses deterministic epsilon insets against coincident-face black patches. It also does sRGB→linear palette conversion, the same class of colour bug we hit in the glTF vertex-colour fix, and exports a scene to three.js JSON by replaying the generator. Directly relevant to the voxel ASMR scenes and voxel model pipeline.
- `blender-staged-scene-construction` (same repo): numbered, checkpointed build stages, `from_pydata` instead of operators in loops, a deterministic `build_all.py` rebuild, and GLB export hygiene. For scenes big enough to freeze Blender.
- `blender-mcp-isolated-sessions` (same repo): start a second blender-mcp on another port without hijacking the Blender that's already running on 9876. Useful when two Claude sessions both need Blender.

---

## Looked at and skipped

| Candidate | Why skipped |
|---|---|
| Qb-Lab **hooks** (UserPromptSubmit / PreToolUse / Stop) | The code is clean: no network calls, and it stays silent outside Godot projects. But the PreToolUse hook **denies every `Write` to a `.tscn` and any edit containing `[node`, `[ext_resource` or `uid://`**, and the Stop hook blocks the turn until headless verify runs. That breaks pipelines that generate scenes and parallel agent teams. The skills carry the same rules as guidance. `godot-verify` still mentions "a Stop hook in this pack"; that hook isn't installed. |
| Qb-Lab design/process skills (grill-me, write-plan, build-loop, session-handoff…) | They duplicate mattpocock-skills and our handoff-doc habit. `game-feel-review`, `streamability`, and `scope-control` are worth a look later. |
| awesome-gamedev's Roblox skills (7), `router` | Overlap with roblox-brain, and two Roblox packs would compete to trigger. The router dispatches to Unity/Unreal/Bevy skills we don't install. |
| awesome-gamedev Unity / Unreal / Bevy / Phaser / three.js / pygame / LÖVE | Not our engines. Reinstall with `--only` after adding them to `skills.json` if that changes. |
| [EL4CTEO/roblox-skills](https://github.com/EL4CTEO/roblox-skills) (23), [luumenlabs/luau-skills](https://github.com/luumenlabs/luau-skills) (9), [afrxo/roblox-agent-skills](https://github.com/afrxo/roblox-agent-skills) (4, Rojo/Fusion) | Solid but smaller, and they overlap roblox-brain. afrxo is the pick if a project goes Rojo + Fusion 0.3. |
| [S4US/Roqer](https://github.com/S4US/Roqer) (17 Roblox skills) | They live inside a desktop agent app (AGPL-3.0), not a standalone skill pack. |
| [CodePhobiia/claude-roblox-game-studio](https://github.com/CodePhobiia/claude-roblox-game-studio), [MRCalderon3D/everything-game-dev-code](https://github.com/MRCalderon3D/everything-game-dev-code) | Whole "studio in a box" scaffolds (36–42 agents, 50–86 skills). They'd take over the project layout and flood the skill list. |
| [Randroids-Dojo/Godot-Claude-Skills](https://github.com/Randroids-Dojo/Godot-Claude-Skills) | Good if a project adopts GdUnit4/PlayGodot. DG3D already has its own `run_tests.gd` runner. |
| [vl4dt/godot-skills](https://github.com/vl4dt/godot-skills), [alexmeckes/godot-claude-skills](https://github.com/alexmeckes/godot-claude-skills) | Covered by awesome-gamedev + Qb-Lab. vl4dt's `godot-47-migration` is worth a look when upgrading an older project. |
| scenario-labs/skills (Blender DCC) | Built around the paid Scenario API. |
| Impertio-Studio Blender/Bonsai pack (73) | Architecture/IFC/BIM, not games. |
| HKUDS/CLI-Anything blender | A different harness (CLI wrapper). We already have the live MCP. |
| `anthropics/skills/mcp-builder` | Fine (Apache-2.0), but `mcp-server-dev` covers the same ground and updates through the marketplace. |
| Official marketplace `unity`, `unreal-engine-skills-for-claude-code` | Wrong engines. There is **no** official Roblox, Godot, or Blender plugin. |

## Gotchas

- **Context cost.** The 59 new skill descriptions add about 15.5k characters (~4k tokens) to every turn's skill listing. That's acceptable, but `/skill-doctor` shows which skills never fire, and those are the first to prune. Installing per project (`--dest`) keeps the Roblox skills out of Godot sessions and the other way round.
- **Frontmatter repair.** Upstream `blender-staged-scene-construction` has an unquoted `Triggers: "…"` in its description, so YAML fails to parse it and the skill lists with only its title (it would never trigger). `install.py` rewrites such descriptions as block scalars and prints `repaired frontmatter: …`.
- **Version pins.** awesome-gamedev targets Godot 4.7, and roblox-brain skills were last reviewed in Aug 2026. If an engine update changes an API, the engine's own docs win (Roblox: `rbx-docs-search`).
- Every pick is plain markdown plus a few reference scripts. No hooks, no network calls, and nothing runs until Claude chooses to.

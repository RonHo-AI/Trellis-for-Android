#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Agent Pipeline Context Injection Hook — Android Trellis Template

Core Design Philosophy:
- Dispatch is a pure dispatcher, only responsible for calling subagents
- Hook injects all context including model routing and Android specs
- Each agent has a dedicated jsonl file defining its context

Android Extensions:
- Model routing: reads model_routing table from config.yaml, overrides 'model' in updatedInput
- Android spec injection: injects relevant spec/design-analysis/, spec/implementation/,
  spec/verification/ files per agent type
- New agents: ui-designer (design token extraction), apply-diff (Codex diff application)

Trigger: PreToolUse (before Task / Agent tool call)
"""

# IMPORTANT: Suppress all warnings FIRST
import warnings
warnings.filterwarnings("ignore")

import json
import os
import sys
from pathlib import Path

# IMPORTANT: Force stdout to use UTF-8 on Windows
# This fixes UnicodeEncodeError when outputting non-ASCII characters
if sys.platform == "win32":
    import io as _io
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    elif hasattr(sys.stdout, "detach"):
        sys.stdout = _io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8", errors="replace")  # type: ignore[union-attr]

# =============================================================================
# Path Constants (change here to rename directories)
# =============================================================================

DIR_WORKFLOW = ".trellis"
DIR_WORKSPACE = "workspace"
DIR_TASKS = "tasks"
DIR_SPEC = "spec"
FILE_CURRENT_TASK = ".current-task"
FILE_TASK_JSON = "task.json"

# Agents that don't update phase (can be called at any time)
AGENTS_NO_PHASE_UPDATE = {"debug", "research", "ui-designer", "apply-diff"}

# =============================================================================
# Subagent Constants (change here to rename subagent types)
# =============================================================================

AGENT_IMPLEMENT = "implement"
AGENT_CHECK = "check"
AGENT_DEBUG = "debug"
AGENT_RESEARCH = "research"
AGENT_UI_DESIGNER = "ui-designer"
AGENT_APPLY_DIFF = "apply-diff"

# Agents that require a task directory
AGENTS_REQUIRE_TASK = (AGENT_IMPLEMENT, AGENT_CHECK, AGENT_DEBUG, AGENT_APPLY_DIFF)
# All supported agents
AGENTS_ALL = (
    AGENT_IMPLEMENT, AGENT_CHECK, AGENT_DEBUG, AGENT_RESEARCH,
    AGENT_UI_DESIGNER, AGENT_APPLY_DIFF,
)

# Maps agent type to model_routing config key
AGENT_TO_ROUTING_KEY: dict[str, str] = {
    AGENT_UI_DESIGNER: "design_analysis",
    "plan": "planning",
    AGENT_IMPLEMENT: "implementation",
    AGENT_APPLY_DIFF: "apply_diff",
    AGENT_CHECK: "verification",
    AGENT_DEBUG: "debugging",
    AGENT_RESEARCH: "research",
}


def find_repo_root(start_path: str) -> str | None:
    """
    Find git repo root from start_path upwards

    Returns:
        Repo root path, or None if not found
    """
    current = Path(start_path).resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return str(current)
        current = current.parent
    return None


def load_model_routing(repo_root: str) -> dict[str, str]:
    """
    Load model routing table from .trellis/config.yaml.

    Returns:
        Dict mapping routing key to model name, e.g. {"verification": "sonnet"}
        Empty dict if config is unavailable.
    """
    config_path = os.path.join(repo_root, DIR_WORKFLOW, "config.yaml")
    if not os.path.exists(config_path):
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Simple nested YAML parser for model_routing section
        routing: dict[str, str] = {}
        in_routing = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                continue
            if line.startswith("model_routing:"):
                in_routing = True
                continue
            if in_routing:
                # Nested key detection: 2+ spaces indent
                if line.startswith("  ") and ":" in stripped and not stripped.startswith("-"):
                    key, _, val = stripped.partition(":")
                    routing[key.strip()] = val.strip()
                elif not line.startswith(" "):
                    # Top-level key — end of model_routing section
                    in_routing = False
        return routing
    except Exception:
        return {}


def get_model_for_agent(repo_root: str, subagent_type: str) -> str | None:
    """
    Look up the model to use for the given agent type.

    Returns model name (e.g. "opus", "sonnet") or None if not configured.
    """
    routing_key = AGENT_TO_ROUTING_KEY.get(subagent_type)
    if not routing_key:
        return None
    routing = load_model_routing(repo_root)
    return routing.get(routing_key)


def get_current_task(repo_root: str) -> str | None:
    """
    Read current task directory path from .trellis/.current-task

    Returns:
        Task directory relative path (relative to repo_root)
        None if not set
    """
    current_task_file = os.path.join(repo_root, DIR_WORKFLOW, FILE_CURRENT_TASK)
    if not os.path.exists(current_task_file):
        return None

    try:
        with open(current_task_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content if content else None
    except Exception:
        return None


def update_current_phase(repo_root: str, task_dir: str, subagent_type: str) -> None:
    """
    Update current_phase in task.json based on subagent_type.

    This ensures phase tracking is always accurate, regardless of whether
    dispatch agent remembers to update it.

    Logic:
    - Read next_action array from task.json
    - Find the next phase whose action matches subagent_type
    - Only move forward, never backward
    - Some agents (debug, research) don't update phase
    """
    if subagent_type in AGENTS_NO_PHASE_UPDATE:
        return

    task_json_path = os.path.join(repo_root, task_dir, FILE_TASK_JSON)
    if not os.path.exists(task_json_path):
        return

    try:
        with open(task_json_path, "r", encoding="utf-8") as f:
            task_data = json.load(f)

        current_phase = task_data.get("current_phase", 0)
        next_actions = task_data.get("next_action", [])

        # Map action names to subagent types
        # "implement" -> "implement", "check" -> "check", "finish" -> "check"
        action_to_agent = {
            "implement": "implement",
            "check": "check",
            "finish": "check",  # finish uses check agent
        }

        # Find the next phase that matches this subagent_type
        new_phase = None
        for action in next_actions:
            phase_num = action.get("phase", 0)
            action_name = action.get("action", "")
            expected_agent = action_to_agent.get(action_name)

            # Only consider phases after current_phase
            if phase_num > current_phase and expected_agent == subagent_type:
                new_phase = phase_num
                break

        if new_phase is not None:
            task_data["current_phase"] = new_phase

            with open(task_json_path, "w", encoding="utf-8") as f:
                json.dump(task_data, f, indent=2, ensure_ascii=False)
    except Exception:
        # Don't fail the hook if phase update fails
        pass


def read_file_content(base_path: str, file_path: str) -> str | None:
    """Read file content, return None if file doesn't exist"""
    full_path = os.path.join(base_path, file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None
    return None


def read_directory_contents(
    base_path: str, dir_path: str, max_files: int = 20
) -> list[tuple[str, str]]:
    """
    Read all .md files in a directory

    Args:
        base_path: Base path (usually repo_root)
        dir_path: Directory relative path
        max_files: Max files to read (prevent huge directories)

    Returns:
        [(file_path, content), ...]
    """
    full_path = os.path.join(base_path, dir_path)
    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        return []

    results = []
    try:
        # Only read .md files, sorted by filename
        md_files = sorted(
            [
                f
                for f in os.listdir(full_path)
                if f.endswith(".md") and os.path.isfile(os.path.join(full_path, f))
            ]
        )

        for filename in md_files[:max_files]:
            file_full_path = os.path.join(full_path, filename)
            relative_path = os.path.join(dir_path, filename)
            try:
                with open(file_full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    results.append((relative_path, content))
            except Exception:
                continue
    except Exception:
        pass

    return results


def read_jsonl_entries(base_path: str, jsonl_path: str) -> list[tuple[str, str]]:
    """
    Read all file/directory contents referenced in jsonl file

    Schema:
        {"file": "path/to/file.md", "reason": "..."}
        {"file": "path/to/dir/", "type": "directory", "reason": "..."}

    Returns:
        [(path, content), ...]
    """
    full_path = os.path.join(base_path, jsonl_path)
    if not os.path.exists(full_path):
        return []

    results = []
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    file_path = item.get("file") or item.get("path")
                    entry_type = item.get("type", "file")

                    if not file_path:
                        continue

                    if entry_type == "directory":
                        # Read all .md files in directory
                        dir_contents = read_directory_contents(base_path, file_path)
                        results.extend(dir_contents)
                    else:
                        # Read single file
                        content = read_file_content(base_path, file_path)
                        if content:
                            results.append((file_path, content))
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return results


def get_agent_context(repo_root: str, task_dir: str, agent_type: str) -> str:
    """
    Get complete context for specified agent

    Prioritize agent-specific jsonl, fallback to spec.jsonl if not exists
    """
    context_parts = []

    # 1. Try agent-specific jsonl
    agent_jsonl = f"{task_dir}/{agent_type}.jsonl"
    agent_entries = read_jsonl_entries(repo_root, agent_jsonl)

    # 2. If agent-specific jsonl doesn't exist or empty, fallback to spec.jsonl
    if not agent_entries:
        agent_entries = read_jsonl_entries(repo_root, f"{task_dir}/spec.jsonl")

    # 3. Add all files from jsonl
    for file_path, content in agent_entries:
        context_parts.append(f"=== {file_path} ===\n{content}")

    return "\n\n".join(context_parts)


def get_implement_context(repo_root: str, task_dir: str) -> str:
    """
    Complete context for Implement Agent

    Read order:
    1. All files in implement.jsonl (dev specs)
    2. prd.md (requirements)
    3. info.md (technical design)
    """
    context_parts = []

    # 1. Read implement.jsonl (or fallback to spec.jsonl)
    base_context = get_agent_context(repo_root, task_dir, "implement")
    if base_context:
        context_parts.append(base_context)

    # 2. Requirements document
    prd_content = read_file_content(repo_root, f"{task_dir}/prd.md")
    if prd_content:
        context_parts.append(f"=== {task_dir}/prd.md (Requirements) ===\n{prd_content}")

    # 3. Technical design
    info_content = read_file_content(repo_root, f"{task_dir}/info.md")
    if info_content:
        context_parts.append(
            f"=== {task_dir}/info.md (Technical Design) ===\n{info_content}"
        )

    # 4. Android: inject implementation spec files
    android_impl_specs = [
        f"{DIR_WORKFLOW}/{DIR_SPEC}/implementation/index.md",
        f"{DIR_WORKFLOW}/{DIR_SPEC}/implementation/overlay-patterns.md",
        f"{DIR_WORKFLOW}/{DIR_SPEC}/implementation/coding-standards.md",
        "specs/design/design-tokens.md",
    ]
    for spec_path in android_impl_specs:
        content = read_file_content(repo_root, spec_path)
        if content:
            context_parts.append(f"=== {spec_path} (Android spec) ===\n{content}")

    return "\n\n".join(context_parts)


def get_check_context(repo_root: str, task_dir: str) -> str:
    """
    Complete context for Check Agent

    Read order:
    1. All files in check.jsonl (check specs + dev specs)
    2. prd.md (for understanding task intent)
    """
    context_parts = []

    # 1. Read check.jsonl (or fallback to spec.jsonl + hardcoded check files)
    check_entries = read_jsonl_entries(repo_root, f"{task_dir}/check.jsonl")

    if check_entries:
        for file_path, content in check_entries:
            context_parts.append(f"=== {file_path} ===\n{content}")
    else:
        # Fallback: use hardcoded check files + spec.jsonl
        check_files = [
            (".claude/commands/trellis/finish-work.md", "Finish work checklist"),
            (".claude/commands/trellis/check-cross-layer.md", "Cross-layer check spec"),
            (".claude/commands/trellis/check.md", "Code quality check spec"),
        ]
        for file_path, description in check_files:
            content = read_file_content(repo_root, file_path)
            if content:
                context_parts.append(f"=== {file_path} ({description}) ===\n{content}")

        # Add spec.jsonl
        spec_entries = read_jsonl_entries(repo_root, f"{task_dir}/spec.jsonl")
        for file_path, content in spec_entries:
            context_parts.append(f"=== {file_path} (Dev spec) ===\n{content}")

    # 2. Requirements document (for understanding task intent)
    prd_content = read_file_content(repo_root, f"{task_dir}/prd.md")
    if prd_content:
        context_parts.append(
            f"=== {task_dir}/prd.md (Requirements - for understanding intent) ===\n{prd_content}"
        )

    # 3. Android: inject verification spec files
    android_check_specs = [
        f"{DIR_WORKFLOW}/{DIR_SPEC}/verification/index.md",
        f"{DIR_WORKFLOW}/{DIR_SPEC}/verification/4-tier-verification.md",
        f"{DIR_WORKFLOW}/{DIR_SPEC}/verification/logcat-analysis.md",
    ]
    for spec_path in android_check_specs:
        content = read_file_content(repo_root, spec_path)
        if content:
            context_parts.append(f"=== {spec_path} (Android spec) ===\n{content}")

    return "\n\n".join(context_parts)


def get_finish_context(repo_root: str, task_dir: str) -> str:
    """
    Complete context for Finish phase (final check before PR)

    Read order:
    1. All files in finish.jsonl (if exists)
    2. Fallback to finish-work.md only (lightweight final check)
    3. update-spec.md (for active spec sync)
    4. prd.md (for verifying requirements are met)
    """
    context_parts = []

    # 1. Try finish.jsonl first
    finish_entries = read_jsonl_entries(repo_root, f"{task_dir}/finish.jsonl")

    if finish_entries:
        for file_path, content in finish_entries:
            context_parts.append(f"=== {file_path} ===\n{content}")
    else:
        # Fallback: only finish-work.md (lightweight)
        finish_work = read_file_content(
            repo_root, ".claude/commands/trellis/finish-work.md"
        )
        if finish_work:
            context_parts.append(
                f"=== .claude/commands/trellis/finish-work.md (Finish checklist) ===\n{finish_work}"
            )

    # 2. Spec update process (for active spec sync)
    update_spec = read_file_content(
        repo_root, ".claude/commands/trellis/update-spec.md"
    )
    if update_spec:
        context_parts.append(
            f"=== .claude/commands/trellis/update-spec.md (Spec update process) ===\n{update_spec}"
        )

    # 3. Requirements document (for verifying requirements are met)
    prd_content = read_file_content(repo_root, f"{task_dir}/prd.md")
    if prd_content:
        context_parts.append(
            f"=== {task_dir}/prd.md (Requirements - verify all met) ===\n{prd_content}"
        )

    return "\n\n".join(context_parts)


def get_debug_context(repo_root: str, task_dir: str) -> str:
    """
    Complete context for Debug Agent

    Read order:
    1. All files in debug.jsonl (specs needed for fixing)
    2. codex-review-output.txt (Codex Review results)
    """
    context_parts = []

    # 1. Read debug.jsonl (or fallback to spec.jsonl + hardcoded check files)
    debug_entries = read_jsonl_entries(repo_root, f"{task_dir}/debug.jsonl")

    if debug_entries:
        for file_path, content in debug_entries:
            context_parts.append(f"=== {file_path} ===\n{content}")
    else:
        # Fallback: use spec.jsonl + hardcoded check files
        spec_entries = read_jsonl_entries(repo_root, f"{task_dir}/spec.jsonl")
        for file_path, content in spec_entries:
            context_parts.append(f"=== {file_path} (Dev spec) ===\n{content}")

        check_files = [
            (".claude/commands/trellis/check.md", "Code quality check spec"),
            (".claude/commands/trellis/check-cross-layer.md", "Cross-layer check spec"),
        ]
        for file_path, description in check_files:
            content = read_file_content(repo_root, file_path)
            if content:
                context_parts.append(f"=== {file_path} ({description}) ===\n{content}")

    # 2. Codex review output (if exists)
    codex_output = read_file_content(repo_root, f"{task_dir}/codex-review-output.txt")
    if codex_output:
        context_parts.append(
            f"=== {task_dir}/codex-review-output.txt (Codex Review Results) ===\n{codex_output}"
        )

    return "\n\n".join(context_parts)


def get_ui_designer_context(repo_root: str) -> str:
    """
    Context for UI Designer Agent (design token extraction).

    Injects:
    1. Design analysis spec files
    2. Current design tokens (if exists)
    """
    context_parts = []

    design_specs = [
        f"{DIR_WORKFLOW}/{DIR_SPEC}/design-analysis/index.md",
        f"{DIR_WORKFLOW}/{DIR_SPEC}/design-analysis/token-extraction.md",
        f"{DIR_WORKFLOW}/{DIR_SPEC}/design-analysis/android-resource-mapping.md",
        "specs/design/design-tokens.md",
    ]
    for spec_path in design_specs:
        content = read_file_content(repo_root, spec_path)
        if content:
            context_parts.append(f"=== {spec_path} ===\n{content}")

    return "\n\n".join(context_parts)


def get_apply_diff_context(repo_root: str, task_dir: str) -> str:
    """
    Context for Apply-Diff Agent (Codex output application).

    Injects:
    1. codex-output.diff from task directory (the diff to apply)
    2. Implementation spec (for validation)
    """
    context_parts = []

    # 1. Codex-generated diff
    diff_content = read_file_content(repo_root, f"{task_dir}/codex-output.diff")
    if diff_content:
        context_parts.append(
            f"=== {task_dir}/codex-output.diff (Codex-generated diff to apply) ===\n{diff_content}"
        )

    # 2. Implementation spec for validation
    impl_index = read_file_content(
        repo_root, f"{DIR_WORKFLOW}/{DIR_SPEC}/implementation/index.md"
    )
    if impl_index:
        context_parts.append(
            f"=== {DIR_WORKFLOW}/{DIR_SPEC}/implementation/index.md (Android impl spec) ===\n{impl_index}"
        )

    return "\n\n".join(context_parts)


def build_implement_prompt(original_prompt: str, context: str) -> str:
    """Build complete prompt for Implement"""
    return f"""# Implement Agent Task

You are the Implement Agent in the Multi-Agent Pipeline.

## Your Context

All the information you need has been prepared for you:

{context}

---

## Your Task

{original_prompt}

---

## Workflow

1. **Understand specs** - All dev specs are injected above, understand them
2. **Understand requirements** - Read requirements document and technical design
3. **Implement feature** - Implement following specs and design
4. **Self-check** - Ensure code quality against check specs

## Important Constraints

- Do NOT execute git commit, only code modifications
- Follow all dev specs injected above
- Report list of modified/created files when done"""


def build_check_prompt(original_prompt: str, context: str) -> str:
    """Build complete prompt for Check"""
    return f"""# Check Agent Task

You are the Check Agent in the Multi-Agent Pipeline (code and cross-layer checker).

## Your Context

All check specs and dev specs you need:

{context}

---

## Your Task

{original_prompt}

---

## Workflow

1. **Get changes** - Run `git diff --name-only` and `git diff` to get code changes
2. **Check against specs** - Check item by item against specs above
3. **Self-fix** - Fix issues directly, don't just report
4. **Run verification** - Run project's lint and typecheck commands

## Important Constraints

- Fix issues yourself, don't just report
- Must execute complete checklist in check specs
- Pay special attention to impact radius analysis (L1-L5)"""


def build_finish_prompt(original_prompt: str, context: str) -> str:
    """Build complete prompt for Finish (final check before PR)"""
    return f"""# Finish Agent Task

You are performing the final check before creating a PR.

## Your Context

Finish checklist and requirements:

{context}

---

## Your Task

{original_prompt}

---

## Workflow

1. **Review changes** - Run `git diff --name-only` to see all changed files
2. **Verify requirements** - Check each requirement in prd.md is implemented
3. **Spec sync** - Analyze whether changes introduce new patterns, contracts, or conventions
   - If new pattern/convention found: read target spec file → update it → update index.md if needed
   - If infra/cross-layer change: follow the 7-section mandatory template from update-spec.md
   - If pure code fix with no new patterns: skip this step
4. **Run final checks** - Execute lint and typecheck
5. **Confirm ready** - Ensure code is ready for PR

## Important Constraints

- You MAY update spec files when gaps are detected (use update-spec.md as guide)
- MUST read the target spec file BEFORE editing (avoid duplicating existing content)
- Do NOT update specs for trivial changes (typos, formatting, obvious fixes)
- If critical CODE issues found, report them clearly (fix specs, not code)
- Verify all acceptance criteria in prd.md are met"""


def build_debug_prompt(original_prompt: str, context: str) -> str:
    """Build complete prompt for Debug"""
    return f"""# Debug Agent Task

You are the Debug Agent in the Multi-Agent Pipeline (issue fixer).

## Your Context

Dev specs and Codex Review results:

{context}

---

## Your Task

{original_prompt}

---

## Workflow

1. **Understand issues** - Analyze issues pointed out in Codex Review
2. **Locate code** - Find positions that need fixing
3. **Fix against specs** - Fix issues following dev specs
4. **Verify fixes** - Run typecheck to ensure no new issues

## Important Constraints

- Do NOT execute git commit, only code modifications
- Run typecheck after each fix to verify
- Report which issues were fixed and which files were modified"""


def get_research_context(repo_root: str, task_dir: str | None) -> str:
    """
    Context for Research Agent

    Research doesn't need much preset context, only needs:
    1. Project structure overview (where spec directories are)
    2. Optional research.jsonl (if there are specific search needs)
    """
    context_parts = []

    # 1. Project structure overview (dynamically discover spec directories)
    spec_path = f"{DIR_WORKFLOW}/{DIR_SPEC}"
    spec_root = Path(repo_root) / DIR_WORKFLOW / DIR_SPEC

    # Build spec tree dynamically
    tree_lines = [f"{spec_path}/"]
    if spec_root.is_dir():
        pkg_dirs = sorted(d for d in spec_root.iterdir() if d.is_dir())
        for i, pkg_dir in enumerate(pkg_dirs):
            is_last = i == len(pkg_dirs) - 1
            prefix = "└── " if is_last else "├── "
            layers = sorted(d.name for d in pkg_dir.iterdir() if d.is_dir())
            layer_info = f" ({', '.join(layers)})" if layers else ""
            tree_lines.append(f"{prefix}{pkg_dir.name}/{layer_info}")

    spec_tree = "\n".join(tree_lines)

    project_structure = f"""## Project Spec Directory Structure

```
{spec_tree}
```

To get structured package info, run: `python3 ./{DIR_WORKFLOW}/scripts/get_context.py --mode packages`

## Search Tips

- Spec files: `{spec_path}/**/*.md`
- Code search: Use Glob and Grep tools
- Tech solutions: Use mcp__exa__web_search_exa or mcp__exa__get_code_context_exa"""

    context_parts.append(project_structure)

    # 2. If task directory exists, try reading research.jsonl (optional)
    if task_dir:
        research_entries = read_jsonl_entries(repo_root, f"{task_dir}/research.jsonl")
        if research_entries:
            context_parts.append(
                "\n## Additional Search Context (from research.jsonl)\n"
            )
            for file_path, content in research_entries:
                context_parts.append(f"=== {file_path} ===\n{content}")

    return "\n\n".join(context_parts)


def build_research_prompt(original_prompt: str, context: str) -> str:
    """Build complete prompt for Research"""
    return f"""# Research Agent Task

You are the Research Agent in the Multi-Agent Pipeline (search researcher).

## Core Principle

**You do one thing: find and explain information.**

You are a documenter, not a reviewer.

## Project Info

{context}

---

## Your Task

{original_prompt}

---

## Workflow

1. **Understand query** - Determine search type (internal/external) and scope
2. **Plan search** - List search steps for complex queries
3. **Execute search** - Execute multiple independent searches in parallel
4. **Organize results** - Output structured report

## Search Tools

| Tool | Purpose |
|------|---------|
| Glob | Search by filename pattern |
| Grep | Search by content |
| Read | Read file content |
| mcp__exa__web_search_exa | External web search |
| mcp__exa__get_code_context_exa | External code/doc search |

## Strict Boundaries

**Only allowed**: Describe what exists, where it is, how it works

**Forbidden** (unless explicitly asked):
- Suggest improvements
- Criticize implementation
- Recommend refactoring
- Modify any files

## Report Format

Provide structured search results including:
- List of files found (with paths)
- Code pattern analysis (if applicable)
- Related spec documents
- External references (if any)"""


def build_ui_designer_prompt(original_prompt: str, context: str) -> str:
    """Build complete prompt for UI Designer (design token extraction)"""
    return f"""# UI Designer Agent Task

You are the UI Designer Agent in the Android Trellis Template pipeline.

## Your Mission

Extract design tokens from screenshots or design specs and output them
as structured Android resource values in `specs/design/design-tokens.md`.

## Design Specs and Context

{context}

---

## Your Task

{original_prompt}

---

## Workflow

1. **Analyze input** - Examine the provided screenshots or design descriptions
2. **Extract tokens** - Identify colors, dimensions, typography, spacing values
3. **Map to Android** - Convert tokens to Android resource types (color, dimen, string)
4. **Write output** - Update `specs/design/design-tokens.md` with extracted tokens

## Token Output Format

```markdown
## Colors
| Token Name | Value | Android Resource |
|------------|-------|-----------------|
| status_bar_bg | #1A1A2E | @color/status_bar_background |

## Dimensions
| Token Name | Value | Android Resource |
|------------|-------|-----------------|
| status_bar_height | 24dp | @dimen/status_bar_height |
```

## Important Constraints

- Output ONLY Android-compatible resource values (no CSS units)
- Use descriptive token names following snake_case convention
- Every token must have a clear Android resource mapping
- Preserve existing tokens when updating `design-tokens.md`"""


def build_apply_diff_prompt(original_prompt: str, context: str) -> str:
    """Build complete prompt for Apply-Diff (Codex output application)"""
    return f"""# Apply-Diff Agent Task

You are the Apply-Diff Agent in the Android Trellis Template pipeline.

## Code Sovereignty Principle

Codex generates diffs. YOU write the files. This preserves Claude Code's
full control over the codebase and enables proper review of all changes.

## Diff and Context

{context}

---

## Your Task

{original_prompt}

---

## Workflow

1. **Read the diff** - Parse `codex-output.diff` carefully (unified diff format)
2. **Validate scope** - Confirm changes are within Android AOSP source or overlay paths
3. **Apply changes** - Use Edit/Write tools to apply each hunk precisely
4. **Verify syntax** - Check modified files for obvious syntax errors
5. **Report result** - List all modified files and any hunks that failed to apply

## Application Rules

- Apply hunks in order, top to bottom within each file
- If a hunk fails (context mismatch), report it — do NOT guess or skip silently
- Preserve exact indentation (4 spaces for AOSP Java/Kotlin)
- Do NOT apply changes outside the expected file paths

## Important Constraints

- Do NOT execute git commit
- Do NOT modify files not mentioned in the diff
- Report all failed hunks clearly with file path and line range"""


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")

    if tool_name not in ("Task", "Agent"):
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    subagent_type = tool_input.get("subagent_type", "")
    original_prompt = tool_input.get("prompt", "")
    cwd = input_data.get("cwd", os.getcwd())

    # Only handle subagent types we care about
    if subagent_type not in AGENTS_ALL:
        sys.exit(0)

    # Find repo root
    repo_root = find_repo_root(cwd)
    if not repo_root:
        sys.exit(0)

    # Get current task directory (research doesn't require it)
    task_dir = get_current_task(repo_root)

    # implement/check/debug need task directory
    if subagent_type in AGENTS_REQUIRE_TASK:
        if not task_dir:
            sys.exit(0)
        # Check if task directory exists
        task_dir_full = os.path.join(repo_root, task_dir)
        if not os.path.exists(task_dir_full):
            sys.exit(0)

        # Update current_phase in task.json (system-level enforcement)
        update_current_phase(repo_root, task_dir, subagent_type)

    # Check for [finish] marker in prompt (check agent with finish context)
    is_finish_phase = "[finish]" in original_prompt.lower()

    # Get context and build prompt based on subagent type
    if subagent_type == AGENT_IMPLEMENT:
        assert task_dir is not None  # validated above
        context = get_implement_context(repo_root, task_dir)
        new_prompt = build_implement_prompt(original_prompt, context)
    elif subagent_type == AGENT_CHECK:
        assert task_dir is not None  # validated above
        if is_finish_phase:
            # Finish phase: use finish context (lighter, focused on final verification)
            context = get_finish_context(repo_root, task_dir)
            new_prompt = build_finish_prompt(original_prompt, context)
        else:
            # Regular check phase: use check context (full specs for self-fix loop)
            context = get_check_context(repo_root, task_dir)
            new_prompt = build_check_prompt(original_prompt, context)
    elif subagent_type == AGENT_DEBUG:
        assert task_dir is not None  # validated above
        context = get_debug_context(repo_root, task_dir)
        new_prompt = build_debug_prompt(original_prompt, context)
    elif subagent_type == AGENT_RESEARCH:
        # Research can work without task directory
        context = get_research_context(repo_root, task_dir)
        new_prompt = build_research_prompt(original_prompt, context)
    elif subagent_type == AGENT_UI_DESIGNER:
        # UI designer doesn't require a task directory
        context = get_ui_designer_context(repo_root)
        new_prompt = build_ui_designer_prompt(original_prompt, context)
    elif subagent_type == AGENT_APPLY_DIFF:
        assert task_dir is not None  # validated above
        context = get_apply_diff_context(repo_root, task_dir)
        new_prompt = build_apply_diff_prompt(original_prompt, context)
    else:
        sys.exit(0)

    if not context:
        sys.exit(0)

    # Build updated input, optionally overriding model via model_routing
    updated_input: dict = {**tool_input, "prompt": new_prompt}
    routed_model = get_model_for_agent(repo_root, subagent_type)
    if routed_model:
        updated_input["model"] = routed_model

    # Return updated input with correct Claude Code PreToolUse format
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": updated_input,
        }
    }

    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()

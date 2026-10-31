#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import shlex
import subprocess
import sys
import tomllib
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SOURCE_ORDER = ("diff", "status", "untracked")


@dataclass
class Step:
    kind: str
    repo: str
    cwd: str
    command: str
    stage: str | None = None
    baseline: dict[str, str] | None = None
    handoff: dict[str, Any] | None = None


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path).expanduser().resolve()
    data = tomllib.loads(config_path.read_text())
    data["__config_path__"] = str(config_path)
    return data


def render_command(template: str, variables: dict[str, str]) -> str:
    return template.format(**variables)


def resolve_root(config: dict[str, Any], root: str | Path | None, branch: str | None = None) -> Path:
    if root is not None:
        return Path(root).expanduser().resolve()

    config_path = Path(config["__config_path__"])
    if config_path.parent.name in (".yongchun", ".codex"):
        fallback = config_path.parent.parent.resolve()
    else:
        fallback = config_path.parent.resolve()
    if branch is None:
        return fallback

    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"], cwd=fallback,
        capture_output=True, text=True,
    )
    if result.returncode:
        return fallback
    worktrees = result.stdout
    current_path: Path | None = None
    for line in worktrees.splitlines() + [""]:
        if line.startswith("worktree "):
            current_path = Path(line.removeprefix("worktree ")).resolve()
        elif line.startswith("branch refs/heads/") and line.removeprefix("branch refs/heads/") == branch:
            return current_path or fallback
    return fallback


def _repo_index(config: dict[str, Any]) -> dict[str, int]:
    return {repo["name"]: index for index, repo in enumerate(config["repos"])}


def _collect_repo_names(repo_map: dict[str, dict[str, Any]], selected: list[str] | None) -> set[str]:
    if selected is None:
        return set(repo_map.keys())
    if not selected:
        return set()

    result: set[str] = set()

    def visit(name: str) -> None:
        if name not in repo_map:
            raise KeyError(f"unknown repo: {name}")
        if name in result:
            return
        result.add(name)
        for dependency in repo_map[name].get("needs", []):
            visit(dependency)

    for repo_name in selected:
        visit(repo_name)
    return result


def select_repos(config: dict[str, Any], selected: list[str] | None) -> list[dict[str, Any]]:
    repo_map = {repo["name"]: repo for repo in config["repos"]}
    selected_names = _collect_repo_names(repo_map, selected)
    if not selected_names:
        return []
    indegree = {name: 0 for name in selected_names}
    children: dict[str, list[str]] = {name: [] for name in selected_names}

    for name in selected_names:
        for dependency in repo_map[name].get("needs", []):
            if dependency not in selected_names:
                continue
            indegree[name] += 1
            children[dependency].append(name)

    order_index = _repo_index(config)
    ready = sorted([name for name, degree in indegree.items() if degree == 0], key=lambda name: order_index[name])
    ordered: list[str] = []

    while ready:
        current = ready.pop(0)
        ordered.append(current)
        for child in sorted(children[current], key=lambda name: order_index[name]):
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
        ready.sort(key=lambda name: order_index[name])

    if len(ordered) != len(selected_names):
        raise ValueError("repo dependency cycle detected")

    return [repo_map[name] for name in ordered]


def select_repo_groups(config: dict[str, Any], selected: list[str] | None) -> list[list[str]]:
    repo_map = {repo["name"]: repo for repo in config["repos"]}
    selected_names = _collect_repo_names(repo_map, selected)
    if not selected_names:
        return []

    indegree = {name: 0 for name in selected_names}
    children: dict[str, list[str]] = {name: [] for name in selected_names}
    for name in selected_names:
        for dependency in repo_map[name].get("needs", []):
            if dependency not in selected_names:
                continue
            indegree[name] += 1
            children[dependency].append(name)

    order_index = _repo_index(config)
    ready = sorted([name for name, degree in indegree.items() if degree == 0], key=lambda name: order_index[name])
    groups: list[list[str]] = []
    visited = 0

    while ready:
        current_group = list(ready)
        groups.append(current_group)
        visited += len(current_group)

        next_ready: list[str] = []
        for current in current_group:
            for child in sorted(children[current], key=lambda name: order_index[name]):
                indegree[child] -= 1
                if indegree[child] == 0:
                    next_ready.append(child)
        ready = sorted(next_ready, key=lambda name: order_index[name])

    if visited != len(selected_names):
        raise ValueError("repo dependency cycle detected")

    return groups


def _repo_path(root: Path, repo: dict[str, Any]) -> Path:
    repo_path = repo["path"]
    return root if repo_path == "." else (root / repo_path)


def _repo_delivery_path(base_worktree: Path, repo: dict[str, Any]) -> Path:
    return _repo_path(base_worktree, repo)


def _root_stage(config: dict[str, Any]) -> str:
    stages = config.get("queue", {}).get("stages", [])
    return stages[-1] if stages else "root-merged"


def _queue_step(config: dict[str, Any], root: Path, command_key: str, variables: dict[str, str], stage: str | None = None) -> Step | None:
    queue = config.get("queue", {})
    template = queue.get(command_key)
    if not template:
        return None
    rendered = render_command(template, variables)
    return Step(kind=f"queue:{command_key}", repo="root", cwd=str(root), command=rendered, stage=stage)


def _config_order(config: dict[str, Any]) -> list[str]:
    return [repo["name"] for repo in config["repos"]]


def empty_changed_paths_by_source() -> dict[str, list[str]]:
    return {source: [] for source in SOURCE_ORDER}


def parse_diff_paths(output: str) -> list[str]:
    return [line.strip() for line in output.splitlines() if line.strip()]


def parse_status_paths_by_source(output: str) -> dict[str, list[str]]:
    paths_by_source = empty_changed_paths_by_source()
    for raw_line in output.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        source = "untracked" if line.startswith("?? ") else "status"
        path_text = line[3:] if len(line) >= 4 else ""
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        path_text = path_text.strip()
        if path_text:
            paths_by_source[source].append(path_text)
    return paths_by_source


def parse_status_paths(output: str) -> list[str]:
    paths_by_source = parse_status_paths_by_source(output)
    return _dedupe(paths_by_source["status"] + paths_by_source["untracked"])


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _find_base_worktree(root: Path, base_branch: str) -> Path:
    try:
        output = _git_output(root, "worktree", "list", "--porcelain")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return root

    current_path: Path | None = None
    for raw_line in output.splitlines():
        if raw_line.startswith("worktree "):
            current_path = Path(raw_line.split(" ", 1)[1]).expanduser().resolve()
            continue
        if raw_line == f"branch refs/heads/{base_branch}" and current_path is not None:
            return current_path
    return root


def _normalize_changed_paths_by_source(raw: dict[str, list[str]] | None) -> dict[str, list[str]]:
    normalized = empty_changed_paths_by_source()
    if not raw:
        return normalized
    for source in SOURCE_ORDER:
        normalized[source] = _dedupe(list(raw.get(source, [])))
    return normalized


def _flatten_changed_paths_by_source(changed_paths_by_source: dict[str, list[str]]) -> list[str]:
    combined: list[str] = []
    for source in SOURCE_ORDER:
        combined.extend(changed_paths_by_source.get(source, []))
    return _dedupe(combined)


def collect_changed_paths_by_source(root: str | Path, base_branch: str, branch: str) -> dict[str, list[str]]:
    root_path = Path(root).expanduser().resolve()
    status_paths = parse_status_paths_by_source(_git_output(root_path, "status", "--porcelain"))
    return _normalize_changed_paths_by_source(
        {
            "diff": parse_diff_paths(_git_output(root_path, "diff", "--name-only", f"{base_branch}...{branch}")),
            "status": status_paths["status"],
            "untracked": status_paths["untracked"],
        }
    )


def collect_changed_paths(root: str | Path, base_branch: str, branch: str) -> list[str]:
    return _flatten_changed_paths_by_source(collect_changed_paths_by_source(root, base_branch, branch))


def _matches_repo_path(candidate: str, repo_path: str) -> bool:
    normalized = repo_path.strip("/").rstrip("/")
    if not normalized or normalized == ".":
        return False
    return candidate == normalized or candidate.startswith(f"{normalized}/")


def _match_repo_for_path(config: dict[str, Any], changed_path: str) -> str | None:
    matched_name: str | None = None
    matched_length = -1
    for repo in config["repos"]:
        repo_path = repo["path"]
        if not _matches_repo_path(changed_path, repo_path):
            continue
        repo_length = len(repo_path.strip("/").rstrip("/"))
        if repo_length > matched_length:
            matched_name = repo["name"]
            matched_length = repo_length
    return matched_name


def _find_root_repo_name(config: dict[str, Any]) -> str | None:
    for repo in config["repos"]:
        if repo.get("path") == "." or repo.get("role") == "root":
            return repo["name"]
    return None


def _expand_repo_names(config: dict[str, Any], direct_names: list[str], detected_only: bool = False) -> list[str]:
    if detected_only or not direct_names:
        return list(direct_names)

    repo_map = {repo["name"]: repo for repo in config["repos"]}
    root_name = _find_root_repo_name(config)
    pending = list(direct_names)
    expanded_set = set(direct_names)

    while pending:
        current = pending.pop(0)
        current_repo = repo_map[current]
        for dependency in current_repo.get("needs", []):
            if dependency in expanded_set:
                continue
            expanded_set.add(dependency)
            pending.append(dependency)

        if config.get("policies", {}).get("api_before_clients") and current_repo.get("sdk_generate"):
            for dependency in current_repo.get("needs", []):
                if dependency in expanded_set:
                    continue
                expanded_set.add(dependency)
                pending.append(dependency)

    if root_name and any(name != root_name for name in expanded_set):
        expanded_set.add(root_name)

    return [repo["name"] for repo in select_repos(config, list(expanded_set))]


def _repo_has_branch(root: str | Path, repo: dict[str, Any], branch: str) -> bool:
    repo_path = _repo_path(Path(root).expanduser().resolve(), repo)
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", branch],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0


def _normalize_repo_detection_sources(repo_detection_sources: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    for repo_name, info in repo_detection_sources.items():
        paths = info.get("paths", {})
        normalized_paths: dict[str, list[str]] = {}
        sources: list[str] = []
        for source in SOURCE_ORDER:
            source_paths = _dedupe(list(paths.get(source, [])))
            if not source_paths:
                continue
            normalized_paths[source] = source_paths
            sources.append(source)
        if sources:
            normalized[repo_name] = {
                "sources": sources,
                "paths": normalized_paths,
            }
    return normalized


def _flatten_repo_detection_sources(repo_detection_sources: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    flattened: dict[str, list[str]] = {}
    for repo_name, info in repo_detection_sources.items():
        all_paths: list[str] = []
        for source in SOURCE_ORDER:
            all_paths.extend(info.get("paths", {}).get(source, []))
        flattened[repo_name] = _dedupe(all_paths)
    return flattened


def detect_repo_selection(config: dict[str, Any], changed_paths: list[str], detected_only: bool = False) -> dict[str, Any]:
    return detect_repo_selection_from_sources(
        config,
        {
            "diff": [],
            "status": changed_paths,
            "untracked": [],
        },
        detected_only=detected_only,
    )


def detect_repo_selection_from_sources(
    config: dict[str, Any],
    changed_paths_by_source: dict[str, list[str]],
    detected_only: bool = False,
) -> dict[str, Any]:
    repo_order = _config_order(config)
    direct_names: list[str] = []
    repo_detection_sources: dict[str, dict[str, Any]] = {}
    unmatched_paths: list[str] = []
    root_name = _find_root_repo_name(config)
    normalized_paths = _normalize_changed_paths_by_source(changed_paths_by_source)

    for source in SOURCE_ORDER:
        for changed_path in normalized_paths[source]:
            repo_name = _match_repo_for_path(config, changed_path)
            if repo_name is None:
                if root_name is None:
                    unmatched_paths.append(changed_path)
                    continue
                repo_name = root_name
            if repo_name not in direct_names:
                direct_names.append(repo_name)
            repo_detection_sources.setdefault(repo_name, {"paths": {}})
            repo_detection_sources[repo_name]["paths"].setdefault(source, []).append(changed_path)

    direct_names.sort(key=repo_order.index)
    expanded_names = _expand_repo_names(config, direct_names, detected_only=detected_only)
    normalized_repo_sources = _normalize_repo_detection_sources(repo_detection_sources)

    return {
        "direct_repos": direct_names,
        "expanded_repos": expanded_names,
        "detection_reasons": _flatten_repo_detection_sources(normalized_repo_sources),
        "changed_paths_by_source": normalized_paths,
        "repo_detection_sources": normalized_repo_sources,
        "unmatched_paths": unmatched_paths,
    }


def refine_detection_for_root_pointer_changes(
    config: dict[str, Any],
    detection: dict[str, Any],
    root: str | Path,
    branch: str,
) -> dict[str, Any]:
    root_name = _find_root_repo_name(config)
    if root_name is None:
        return detection

    repo_map = {repo["name"]: repo for repo in config["repos"]}
    updated_repo_sources = {
        name: {
            "paths": {
                source: list(paths)
                for source, paths in info.get("paths", {}).items()
            }
        }
        for name, info in detection.get("repo_detection_sources", {}).items()
    }

    for repo_name in list(updated_repo_sources.keys()):
        if repo_name == root_name:
            continue
        repo = repo_map[repo_name]
        repo_path = repo["path"].strip("/").rstrip("/")
        if not repo_path:
            continue

        if _repo_has_branch(root, repo, branch):
            continue

        repo_paths = updated_repo_sources[repo_name]["paths"]
        moved_any = False
        for source in SOURCE_ORDER:
            source_paths = list(repo_paths.get(source, []))
            direct_pointer_hits = [path for path in source_paths if path == repo_path]
            if not direct_pointer_hits:
                continue
            repo_paths[source] = [path for path in source_paths if path != repo_path]
            if not repo_paths[source]:
                repo_paths.pop(source, None)
            updated_repo_sources.setdefault(root_name, {"paths": {}})
            updated_repo_sources[root_name]["paths"].setdefault(source, []).extend(direct_pointer_hits)
            moved_any = True
        if moved_any and not repo_paths:
            del updated_repo_sources[repo_name]

    normalized_repo_sources = _normalize_repo_detection_sources(updated_repo_sources)
    direct_repos = sorted(normalized_repo_sources.keys(), key=_config_order(config).index)
    expanded_repos = _expand_repo_names(config, direct_repos, detected_only=False)

    return {
        "direct_repos": direct_repos,
        "expanded_repos": expanded_repos if direct_repos else [],
        "detection_reasons": _flatten_repo_detection_sources(normalized_repo_sources),
        "changed_paths_by_source": detection.get("changed_paths_by_source", empty_changed_paths_by_source()),
        "repo_detection_sources": normalized_repo_sources,
        "unmatched_paths": detection["unmatched_paths"],
    }


def build_plan_steps(config: dict[str, Any], branch: str, selected_repos: list[str] | None, root: str | Path | None = None) -> list[Step]:
    if config.get("queue", {}).get("release_after_merge"):
        return _build_split_plan(config, branch, selected_repos, root)
    root_path = resolve_root(config, root, branch)
    base_branch = config["project"]["base_branch"]
    variables = {
        "branch": branch,
        "base_branch": base_branch,
        "stage": "",
    }
    queue = config.get("queue", {})
    delivery = config.get("delivery", {})

    repos = select_repos(config, selected_repos)
    if not repos:
        return []

    steps: list[Step] = []
    if queue.get("enabled"):
        for key in ("enqueue", "claim"):
            step = _queue_step(config, root_path, key, variables)
            if step:
                steps.append(step)
    has_root_repo = False
    base_worktree = _find_base_worktree(root_path, base_branch)

    # Synchronize all merge targets before module verification, including modules
    # whose own config entry does not merge (e.g. Flutter inside the root repo).
    baseline_steps: dict[str, Step] = {}
    for repo in sorted(repos, key=lambda item: item.get("path") != "."):
        if not repo.get("merge_base"):
            continue
        step = Step(
            kind="baseline-sync", repo=repo["name"], cwd=str(_repo_path(root_path, repo)),
            command=f"sync {branch} onto local {base_branch}",
            baseline={"branch": branch, "base_branch": base_branch,
                      "base_cwd": str(_repo_delivery_path(base_worktree, repo))},
        )
        baseline_steps[repo["name"]] = step
        steps.append(step)

    for repo in repos:
        repo_name = repo["name"]
        repo_path = _repo_path(root_path, repo)
        is_root_repo = repo.get("role") == "root" or repo.get("path") == "."
        repo_delivery_path = _repo_delivery_path(base_worktree, repo)
        repo_variables = {**variables, "repo_path": repo["path"]}
        has_root_repo = has_root_repo or is_root_repo

        for command in repo.get("verify", []):
            steps.append(Step(kind="verify", repo=repo_name, cwd=str(repo_path), command=render_command(command, repo_variables)))
        if repo.get("queue_advance_after_verify"):
            stage = repo["queue_advance_after_verify"]
            step = _queue_step(config, root_path, "advance", {**variables, "stage": stage}, stage=stage)
            if step:
                steps.append(step)

        sdk_command = repo.get("sdk_generate")
        if sdk_command:
            steps.append(Step(kind="sdk-generate", repo=repo_name, cwd=str(repo_path), command=render_command(sdk_command, repo_variables)))
        if repo.get("queue_advance_after_sdk"):
            stage = repo["queue_advance_after_sdk"]
            step = _queue_step(config, root_path, "advance", {**variables, "stage": stage}, stage=stage)
            if step:
                steps.append(step)

        if repo.get("merge_base"):
            baseline_step = baseline_steps[repo_name]
            steps.append(Step(
                kind="baseline-check", repo=repo_name, cwd=str(repo_path),
                command=f"check verified {branch} and unchanged {base_branch}",
                baseline=baseline_step.baseline,
            ))
            command = render_command(delivery["merge_base"], variables)
            steps.append(Step(kind="merge-base", repo=repo_name, cwd=str(repo_delivery_path), command=command))
        if repo.get("queue_advance_after_merge"):
            stage = repo["queue_advance_after_merge"]
            step = _queue_step(config, root_path, "advance", {**variables, "stage": stage}, stage=stage)
            if step:
                steps.append(step)

        if repo.get("push_base"):
            command = render_command(delivery["push_base"], variables)
            steps.append(Step(kind="push-base", repo=repo_name, cwd=str(repo_delivery_path), command=command))

        deploy_command = repo.get("deploy")
        if deploy_command:
            steps.append(Step(kind="deploy", repo=repo_name, cwd=str(root_path), command=render_command(deploy_command, repo_variables)))
        if repo.get("queue_advance_after_deploy"):
            stage = repo["queue_advance_after_deploy"]
            step = _queue_step(config, root_path, "advance", {**variables, "stage": stage}, stage=stage)
            if step:
                steps.append(step)

        upload_command = repo.get("upload")
        if upload_command:
            steps.append(Step(kind="upload", repo=repo_name, cwd=str(root_path), command=render_command(upload_command, repo_variables)))
        if repo.get("queue_advance_after_upload"):
            stage = repo["queue_advance_after_upload"]
            step = _queue_step(config, root_path, "advance", {**variables, "stage": stage}, stage=stage)
            if step:
                steps.append(step)

        for command in repo.get("post_delivery_checks", []):
            steps.append(Step(kind="post-check", repo=repo_name, cwd=str(root_path), command=render_command(command, repo_variables)))

    if queue.get("enabled") and has_root_repo:
        final_stage = _root_stage(config)
        for key, stage in (
            ("root_merged_checklist", None),
            ("mark_root_merged", final_stage),
            ("require_stage", final_stage),
            ("finish", final_stage),
            ("status", None),
        ):
            step = _queue_step(config, root_path, key, {**variables, "stage": final_stage}, stage=stage)
            if step:
                steps.append(step)

    clean_template = config.get("worktree", {}).get("clean")
    if has_root_repo and clean_template:
        steps.append(
            Step(
                kind="worktree-clean",
                repo="root",
                cwd=str(base_worktree),
                command=render_command(clean_template, variables),
            )
        )

    return steps


def _build_split_plan(config: dict[str, Any], branch: str, selected: list[str] | None, root: str | Path | None) -> list[Step]:
    root_path = resolve_root(config, root, branch)
    base_branch = config["project"]["base_branch"]
    base = _find_base_worktree(root_path, base_branch)
    repos = select_repos(config, selected)
    roots = [repo for repo in repos if repo["path"] == "." and repo.get("merge_base")]
    if len(roots) != 1 or not config.get("queue", {}).get("enabled"):
        raise ValueError("Merge-only queue requires an enabled queue and exactly one root merge target")
    clean = config.get("worktree", {}).get("clean")
    if not clean:
        raise ValueError("Merge-only queue requires worktree.clean before release_after_merge")
    variables = {"branch": branch, "base_branch": base_branch, "commit": "{commit}", "manifest": "{manifest}", "stage": ""}
    handoff_repos = []
    for repo in repos:
        commands = []
        repo_vars = {**variables, "repo_path": repo["path"]}
        if repo.get("push_base"):
            delivery = config.get("delivery", {})
            if delivery.get("push_base", "git push origin {base_branch}") != "git push origin {base_branch}" and not delivery.get("push_commit"):
                raise ValueError("Custom push_base requires delivery.push_commit for independent delivery")
            commands.append(delivery.get("push_commit", "git push origin {commit}:refs/heads/{base_branch}"))
        commands.extend(repo[key] for key in ("deploy", "upload") if repo.get(key))
        commands.extend(repo.get("post_delivery_checks", []))
        if any("{commit}" not in command for command in commands):
            raise ValueError(f"Independent delivery for {repo['name']} requires {{commit}} in every push/deploy/upload/check command")
        handoff_repos.append({"name": repo["name"], "source": str(_repo_delivery_path(base, repo)),
                              "commands": [render_command(command, repo_vars) for command in commands]})
    enqueue = config.get("post_merge", {}).get("enqueue")
    if any(repo["commands"] for repo in handoff_repos) and (not enqueue or "{manifest}" not in enqueue):
        raise ValueError("Independent delivery requires post_merge.enqueue with {manifest}")

    # Reuse dependency ordering and baseline checks, retaining only local merge work.
    merge_config = copy.deepcopy(config)
    for key in ("release_after_merge", "root_merged_checklist", "mark_root_merged", "require_stage", "finish", "status"):
        merge_config["queue"].pop(key, None)
    merge_config["worktree"].pop("clean", None)
    for repo in merge_config["repos"]:
        for key in ("push_base", "deploy", "upload", "post_delivery_checks", "queue_advance_after_deploy", "queue_advance_after_upload"):
            repo.pop(key, None)
    steps = build_plan_steps(merge_config, branch, selected, root=root_path)
    root_merge = next(i for i, step in enumerate(steps) if step.kind == "merge-base" and step.repo == roots[0]["name"])
    if any(step.kind in ("verify", "sdk-generate", "baseline-check", "merge-base") for step in steps[root_merge + 1:]):
        raise ValueError("All task verification and child merges must precede the root merge before immediate cleanup")
    steps.append(Step(kind="record-handoff", repo=roots[0]["name"], cwd=str(base), command="record immutable merged commits",
                      handoff={"branch": branch, "base_branch": base_branch, "repos": handoff_repos}))
    steps.append(Step(kind="worktree-clean", repo=roots[0]["name"], cwd=str(base), command=render_command(clean, variables)))
    steps.append(Step(kind="queue:release_after_merge", repo=roots[0]["name"], cwd=str(base),
                      command=render_command(config["queue"]["release_after_merge"], variables)))
    if config["queue"].get("status"):
        steps.append(_queue_step(config, base, "status", variables))
    if enqueue:
        steps.append(Step(kind="post-merge-enqueue", repo=roots[0]["name"], cwd=str(base), command=render_command(enqueue, variables)))
    return steps


def _record_handoff(step: Step, baselines: dict[str, tuple[str, str]]) -> tuple[Path, str]:
    assert step.handoff is not None
    job = copy.deepcopy(step.handoff)
    job.update({"version": 1, "id": uuid.uuid4().hex, "status": "awaiting-release"})
    root_commit = ""
    for repo in job["repos"]:
        source = Path(repo["source"])
        commit = _git_output(source, "rev-parse", "HEAD").strip()
        if repo["name"] in baselines and commit != baselines[repo["name"]][1]:
            raise RuntimeError(f"Merged commit changed before handoff for {repo['name']}")
        repo["commit"] = commit
        repo["commands"] = [command.replace("{commit}", commit) for command in repo["commands"]]
        if repo["name"] == step.repo:
            root_commit = commit
    common = (Path(step.cwd) / _git_output(Path(step.cwd), "rev-parse", "--git-common-dir").strip()).resolve()
    directory = common / "delivery-jobs"
    directory.mkdir(exist_ok=True)
    path = directory / f"{job['id']}.json"
    _write_handoff(path, job)
    print(f"Post-merge handoff: {path}")
    return path, root_commit


def _write_handoff(path: Path, job: dict[str, Any]) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(job, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def plan_payload(
    config: dict[str, Any],
    branch: str,
    selected_repos: list[str] | None,
    root: str | Path | None = None,
    auto_detect: bool = True,
    detected_only: bool = False,
) -> dict[str, Any]:
    root_path = resolve_root(config, root, branch)
    detection = {
        "direct_repos": [],
        "expanded_repos": [],
        "detection_reasons": {},
        "changed_paths_by_source": empty_changed_paths_by_source(),
        "repo_detection_sources": {},
        "unmatched_paths": [],
    }
    effective_repos = selected_repos

    if selected_repos is None and auto_detect:
        changed_paths_by_source = collect_changed_paths_by_source(root_path, config["project"]["base_branch"], branch)
        detection = detect_repo_selection_from_sources(config, changed_paths_by_source, detected_only=detected_only)
        if not detected_only:
            detection = refine_detection_for_root_pointer_changes(config, detection, root_path, branch)
        effective_repos = detection["expanded_repos"]
    elif selected_repos is not None:
        detection["expanded_repos"] = list(selected_repos)

    repos = select_repos(config, effective_repos)
    repo_groups = select_repo_groups(config, effective_repos)
    steps = build_plan_steps(config, branch, effective_repos, root=root_path)
    return {
        "project": config["project"]["name"],
        "branch": branch,
        "base_branch": config["project"]["base_branch"],
        "root": str(root_path),
        "repos": [repo["name"] for repo in repos],
        "repo_groups": repo_groups,
        "detected_repos": detection["direct_repos"],
        "expanded_repos": detection["expanded_repos"],
        "detection_reasons": detection["detection_reasons"],
        "changed_paths_by_source": detection["changed_paths_by_source"],
        "repo_detection_sources": detection["repo_detection_sources"],
        "unmatched_paths": detection["unmatched_paths"],
        "steps": [asdict(step) for step in steps],
    }


def print_plan(payload: dict[str, Any]) -> None:
    print(f"Project: {payload['project']}")
    print(f"Branch: {payload['branch']}")
    print(f"Base: {payload['base_branch']}")
    print(f"Root: {payload['root']}")
    print("Repos:", ", ".join(payload["repos"]))
    repo_groups = payload.get("repo_groups", [])
    if repo_groups:
        rendered_groups = " -> ".join(f"[{', '.join(group)}]" for group in repo_groups)
        print(f"Repo groups: {rendered_groups}")
    for line in render_detection_summary(payload):
        print(line)
    print("")
    for index, step in enumerate(payload["steps"], start=1):
        stage_suffix = f" [{step['stage']}]" if step.get("stage") else ""
        print(f"{index}. {step['kind']}{stage_suffix}")
        print(f"   cwd: {step['cwd']}")
        print(f"   cmd: {step['command']}")


def render_detection_summary(payload: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    repo_detection_sources = payload.get("repo_detection_sources", {})
    detected_repos = payload.get("detected_repos", [])
    expanded_repos = payload.get("expanded_repos", [])
    if detected_repos:
        summary = ", ".join(
            f"{repo} [{','.join(repo_detection_sources.get(repo, {}).get('sources', []))}]"
            for repo in detected_repos
        )
        lines.append(f"Detected: {summary}")
        for repo in detected_repos:
            source_parts: list[str] = []
            repo_info = repo_detection_sources.get(repo, {})
            for source in repo_info.get("sources", []):
                source_paths = ",".join(repo_info.get("paths", {}).get(source, []))
                source_parts.append(f"{source}={source_paths}")
            if source_parts:
                lines.append(f"{repo}: {'; '.join(source_parts)}")
    expanded_only = [repo for repo in expanded_repos if repo not in detected_repos]
    if expanded_only:
        lines.append(f"Expanded only: {', '.join(expanded_only)}")
    unmatched_paths = payload.get("unmatched_paths", [])
    if unmatched_paths:
        lines.append(f"Unmatched: {', '.join(unmatched_paths)}")
    return lines


def _check_checkout(path: Path, branch: str) -> None:
    current = _git_output(path, "symbolic-ref", "--quiet", "--short", "HEAD").strip()
    if current != branch:
        raise RuntimeError(f"Expected branch {branch} in checkout {path}, found {current}")
    for name in ("rebase-merge", "rebase-apply", "MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "sequencer"):
        git_path = _git_output(path, "rev-parse", "--git-path", name).strip()
        if (path / git_path).exists():
            raise RuntimeError(f"Unfinished Git operation in {path}: {name}")
    if _git_output(path, "status", "--porcelain").strip():
        raise RuntimeError(f"A clean checkout is required: {path}; commit or resolve changes first")


def _baseline_heads(step: Step) -> tuple[str, str]:
    assert step.baseline is not None
    task = Path(step.cwd)
    base = Path(step.baseline["base_cwd"])
    return (
        _git_output(base, "rev-parse", f"refs/heads/{step.baseline['base_branch']}").strip(),
        _git_output(task, "rev-parse", f"refs/heads/{step.baseline['branch']}").strip(),
    )


def _sync_baseline(step: Step) -> tuple[str, str]:
    assert step.baseline is not None
    task = Path(step.cwd)
    base = Path(step.baseline["base_cwd"])
    branch, base_branch = step.baseline["branch"], step.baseline["base_branch"]
    if branch == base_branch:
        raise RuntimeError("Task branch must differ from the base branch")
    _check_checkout(task, branch)
    _check_checkout(base, base_branch)
    task_common = (task / _git_output(task, "rev-parse", "--git-common-dir").strip()).resolve()
    base_common = (base / _git_output(base, "rev-parse", "--git-common-dir").strip()).resolve()
    if task_common != base_common:
        raise RuntimeError(f"Task and base checkouts must share a Git repository: {task}, {base}")
    base_head, task_head = _baseline_heads(step)
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base_head, task_head], cwd=task,
        capture_output=True, text=True,
    )
    if ancestor.returncode == 1:
        # Refuse unrelated histories, and preserve any merge topology on the task.
        _git_output(task, "merge-base", base_head, task_head)
        subprocess.run(
            ["git", "rebase", "--no-autostash", "--no-update-refs", "--rebase-merges", base_head],
            cwd=task, check=True,
        )
    elif ancestor.returncode:
        raise subprocess.CalledProcessError(ancestor.returncode, ancestor.args, ancestor.stdout, ancestor.stderr)
    heads = _baseline_heads(step)
    if heads[0] != base_head:
        raise RuntimeError(f"Base branch changed during synchronization: {base_branch}; stop and inspect queue ownership")
    print(f"Baseline {step.repo}: {heads[0]}; task: {heads[1]}")
    return heads


def _preflight_baseline(step: Step) -> None:
    assert step.baseline is not None
    task = Path(step.cwd)
    base = Path(step.baseline["base_cwd"])
    branch, base_branch = step.baseline["branch"], step.baseline["base_branch"]
    if branch == base_branch:
        raise RuntimeError("Task branch must differ from the base branch")
    _check_checkout(task, branch)
    _check_checkout(base, base_branch)
    task_common = (task / _git_output(task, "rev-parse", "--git-common-dir").strip()).resolve()
    base_common = (base / _git_output(base, "rev-parse", "--git-common-dir").strip()).resolve()
    if task_common != base_common:
        raise RuntimeError(f"Task and base checkouts must share a Git repository: {task}, {base}")


def _check_baseline(step: Step, expected: tuple[str, str]) -> None:
    assert step.baseline is not None
    actual = _baseline_heads(step)
    if actual != expected:
        raise RuntimeError(
            f"Base or task branch changed after synchronization for {step.repo}: "
            f"expected {expected}, found {actual}; verification is stale. Keep the queue item active."
        )
    _check_checkout(Path(step.cwd), step.baseline["branch"])
    _check_checkout(Path(step.baseline["base_cwd"]), step.baseline["base_branch"])


def run_steps(
    steps: list[Step],
    dry_run: bool = False,
    failure_context_lines: list[str] | None = None,
    root: str | Path | None = None,
    branch: str | None = None,
) -> None:
    total = len(steps)
    cleanup_before_release = any(step.kind == "queue:release_after_merge" for step in steps)
    baselines: dict[str, tuple[str, str]] = {}
    manifest: Path | None = None
    merged_commit = ""
    released = False
    if not dry_run:
        if root is not None and branch is not None:
            _check_checkout(Path(root), branch)
        for step in steps:
            if step.kind == "baseline-sync":
                _preflight_baseline(step)
    for index, step in enumerate(steps, start=1):
        stage_suffix = f" [{step.stage}]" if step.stage else ""
        print(f"[{index}/{total}] {step.kind}{stage_suffix} @ {step.cwd}")
        print(f"{'[internal]' if step.baseline or step.handoff else '$'} {step.command}")
        if dry_run:
            continue
        try:
            if step.kind == "baseline-sync":
                baselines[step.repo] = _sync_baseline(step)
            elif step.kind == "baseline-check":
                if step.repo not in baselines:
                    raise RuntimeError(f"Missing synchronized baseline for {step.repo}; cannot resume at merge")
                _check_baseline(step, baselines[step.repo])
            elif step.kind == "record-handoff":
                manifest, merged_commit = _record_handoff(step, baselines)
            else:
                command = step.command
                if step.kind in ("queue:release_after_merge", "post-merge-enqueue"):
                    if manifest is None:
                        raise RuntimeError("Missing durable handoff; cannot release or enqueue independent delivery")
                    command = command.replace("{manifest}", shlex.quote(str(manifest))).replace("{commit}", merged_commit)
                subprocess.run(command, cwd=step.cwd, shell=True, check=True)
                if step.kind == "queue:release_after_merge":
                    released = True
                    job = json.loads(manifest.read_text())
                    job["status"] = "ready"
                    _write_handoff(manifest, job)
        except (subprocess.CalledProcessError, RuntimeError) as exc:
            if step.kind == "worktree-clean" and not cleanup_before_release:
                print(f"CLEANUP FAILED: {step.command}", file=sys.stderr)
                print(f"CWD: {step.cwd}", file=sys.stderr)
                print(f"EXIT CODE: {exc.returncode}", file=sys.stderr)
                continue
            print(f"FAILED: {step.command}", file=sys.stderr)
            print(f"CWD: {step.cwd}", file=sys.stderr)
            if isinstance(exc, subprocess.CalledProcessError):
                print(f"EXIT CODE: {exc.returncode}", file=sys.stderr)
                print(f"FAILED COMMAND: {exc.cmd}", file=sys.stderr)
            else:
                print(str(exc), file=sys.stderr)
            if released:
                print(f"Merge queue already released. Resume only pending post-release actions using {manifest}; do not rerun merge delivery.", file=sys.stderr)
            if failure_context_lines:
                for line in failure_context_lines:
                    print(line, file=sys.stderr)
            raise


def parse_repo_list(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    return [item.strip() for item in raw.split(",") if item.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plan or run a queue-gated worktree delivery workflow.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("plan", "run"):
        subparser = subparsers.add_parser(name)
        subparser.add_argument("--config", required=True)
        subparser.add_argument("--branch", required=True)
        subparser.add_argument("--root")
        subparser.add_argument("--repos")
        subparser.add_argument("--no-auto-detect", action="store_true")
        subparser.add_argument("--detected-only", action="store_true")
        subparser.add_argument("--json", action="store_true")
        if name == "run":
            subparser.add_argument("--dry-run", action="store_true")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(args.config)
    if args.command == "run" and not config.get("queue", {}).get("release_after_merge"):
        raise SystemExit("Migrate queue.release_after_merge, worktree.clean and pinned post_merge.enqueue before run; legacy full-delivery queue execution is disabled. Use plan to inspect the old configuration.")
    selected_repos = parse_repo_list(args.repos)
    payload = plan_payload(
        config,
        args.branch,
        selected_repos,
        root=args.root,
        auto_detect=not args.no_auto_detect,
        detected_only=args.detected_only,
    )

    if args.command == "plan":
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_plan(payload)
        return

    if not payload["repos"]:
        raise SystemExit("No repos selected for delivery. Pass --repos or create detectable changes first.")

    steps = [Step(**step) for step in payload["steps"]]
    failure_context_lines = render_detection_summary(payload)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_plan(payload)
        print("")
    run_steps(steps, dry_run=args.dry_run, failure_context_lines=failure_context_lines,
              root=payload["root"], branch=args.branch)


if __name__ == "__main__":
    main()

import os, sys
from pathlib import Path
from fabric_cicd import (
    FabricWorkspace,
    publish_all_items,
    unpublish_all_orphan_items,
    change_log_level,
)

# Live logs in GitHub Actions
sys.stdout.reconfigure(line_buffering=True, write_through=True)
sys.stderr.reconfigure(line_buffering=True, write_through=True)

if os.getenv("ACTIONS_STEP_DEBUG", "false").lower() == "true":
    change_log_level("DEBUG")

# The repo root (one level above .deploy/)
root = Path(__file__).resolve().parents[2]
repo_dir = root / os.getenv("REPOSITORY_DIRECTORY", ".")  # "." means repo root

workspace_id = os.getenv("FABRIC_WORKSPACE_ID", "").strip()
if not workspace_id:
    raise SystemExit("FABRIC_WORKSPACE_ID is required but not set.")

environment = os.getenv("FABRIC_ENVIRONMENT", "DEV").strip().upper()
items_raw = os.getenv("ITEMS_IN_SCOPE", "")
items = [i.strip() for i in items_raw.split(",") if i.strip()] or [
    "Notebook", "DataPipeline", "Lakehouse"
]

print(f"[fabric-cicd] Repo dir: {repo_dir}")
print(f"[fabric-cicd] Workspace: {workspace_id} | Env: {environment} | Scope: {items}")

if not repo_dir.exists():
    raise SystemExit(f"Repository directory '{repo_dir}' not found.")

# explicitly point to parameter.yml
find_replace_file = str(Path(__file__).resolve().parents[1] / "parameter.yml")

ws = FabricWorkspace(
    workspace_id=workspace_id,
    environment=environment,
    repository_directory=str(repo_dir),
    item_type_in_scope=items,
    parameter_file_path=find_replace_file,
)

publish_all_items(ws)

if os.getenv("UNPUBLISH_ORPHANS", "false").lower() == "true":
    print("[fabric-cicd] Unpublishing orphan items…")
    unpublish_all_orphan_items(ws)

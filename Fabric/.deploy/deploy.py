import os
import sys
from pathlib import Path
from fabric_cicd import (
    FabricWorkspace,
    publish_all_items,
    unpublish_all_orphan_items,
    change_log_level,
)

# Flush logs immediately
sys.stdout.reconfigure(line_buffering=True, write_through=True)
sys.stderr.reconfigure(line_buffering=True, write_through=True)

if os.getenv("ACTIONS_STEP_DEBUG", "false").lower() == "true":
    change_log_level("DEBUG")

# === Repo paths ===
repo_dir = Path(__file__).resolve().parents[1]   # "Fabric" root
parameter_file = Path(__file__).resolve().parent / "parameter.yml"

workspace_id = os.getenv("FABRIC_WORKSPACE_ID", "").strip()
if not workspace_id:
    raise SystemExit("❌ FABRIC_WORKSPACE_ID is required but not set.")

environment = os.getenv("FABRIC_ENVIRONMENT", "DEV").strip().upper()
items_raw = os.getenv("ITEMS_IN_SCOPE", "")
items = [i.strip() for i in items_raw.split(",") if i.strip()] or [
    "Notebook", "Lakehouse", "SemanticModel", "Report"
]

if not repo_dir.exists():
    raise SystemExit(f"❌ Repository directory '{repo_dir}' not found.")
if not parameter_file.exists():
    raise SystemExit(f"❌ Parameter file '{parameter_file}' not found.")

print(f"[fabric-cicd] Repo dir   : {repo_dir}")
print(f"[fabric-cicd] Workspace : {workspace_id}")
print(f"[fabric-cicd] Env       : {environment}")
print(f"[fabric-cicd] Scope     : {items}")
print(f"[fabric-cicd] Param     : {parameter_file}")

# === Init FabricWorkspace ===
ws = FabricWorkspace(
    workspace_id=workspace_id,
    environment=environment,
    repository_directory=str(repo_dir),
    item_type_in_scope=items,
    parameter_file_path=str(parameter_file),
)

# === Deploy ===
publish_all_items(ws)

# === Cleanup orphaned items (optional) ===
if os.getenv("UNPUBLISH_ORPHANS", "false").lower() == "true":
    print("[fabric-cicd] 🧹 Unpublishing orphan items…")
    unpublish_all_orphan_items(ws)

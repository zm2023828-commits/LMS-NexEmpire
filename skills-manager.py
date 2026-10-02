#!/usr/bin/env python3
"""
Antigravity Skills Manager for NeXEmpire LMS
Enables managing 300+ agent skills from rmyndharis/antigravity-skills catalog
Supports instant local vault installation as well as remote fallback.
"""

import sys
import os
import shutil
import json

# Terminal utf-8 configuration
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

VAULT_DIR = r"C:\Users\JOGNO\.gemini\skills-vault"
WORKSPACE_SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".agents", "skills"))
GLOBAL_SKILLS_DIR = os.path.expanduser(r"C:\Users\JOGNO\.gemini\config\skills")

def get_catalog():
    cat_path = os.path.join(VAULT_DIR, "catalog.json")
    if os.path.exists(cat_path):
        with open(cat_path, "r", encoding="utf-8") as f:
            return json.load(f)
    print("Catalog not found in local vault.")
    return None

def get_bundles():
    bundle_path = os.path.join(VAULT_DIR, "bundles.json")
    if os.path.exists(bundle_path):
        with open(bundle_path, "r", encoding="utf-8") as f:
            return json.load(f).get("bundles", {})
    return {}

def list_skills(filter_str=""):
    cat = get_catalog()
    if not cat:
        return
    skills = cat.get("skills", [])
    count = 0
    print(f"\n{'='*70}\nAvailable Antigravity Skills ({len(skills)} in catalog)\n{'='*70}")
    for s in skills:
        sid = s.get("id", "")
        desc = s.get("description", "")
        if filter_str.lower() in sid.lower() or filter_str.lower() in desc.lower():
            count += 1
            print(f"- {sid:<45} : {desc[:75]}...")
    print(f"\nShowing {count} skills (filter: '{filter_str}').\n")

def search_skills(term):
    if not term:
        print("Usage: python skills-manager.py search <term>")
        return
    list_skills(term)

def install_skill(skill_id, is_global=False):
    target_base = GLOBAL_SKILLS_DIR if is_global else WORKSPACE_SKILLS_DIR
    src_dir = os.path.join(VAULT_DIR, "skills", skill_id)
    
    if not os.path.exists(src_dir):
        print(f"Error: Skill '{skill_id}' not found in vault.")
        # Try finding closest matches
        cat = get_catalog()
        if cat:
            matches = [s['id'] for s in cat.get('skills', []) if skill_id.lower() in s['id'].lower()]
            if matches:
                print("Did you mean one of these?")
                for m in matches[:5]:
                    print(f"  - {m}")
        return False

    dest_dir = os.path.join(target_base, skill_id)
    os.makedirs(target_base, exist_ok=True)
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    shutil.copytree(src_dir, dest_dir)
    scope = "global (~/.gemini/config/skills)" if is_global else f"workspace (.agents/skills)"
    print(f"SUCCESS: Installed '{skill_id}' to {scope} -> {dest_dir}")
    return True

def install_bundle(bundle_name, is_global=False):
    bundles = get_bundles()
    if bundle_name not in bundles:
        print(f"Bundle '{bundle_name}' not found. Available bundles:")
        for b in bundles.keys():
            print(f"  - {b}")
        return
    
    b_data = bundles[bundle_name]
    skills = b_data.get("skills", [])
    print(f"Installing bundle '{bundle_name}' ({len(skills)} skills)...")
    for s in skills:
        install_skill(s, is_global)
    print(f"Bundle '{bundle_name}' installation complete.")

def list_installed(is_global=False):
    target_base = GLOBAL_SKILLS_DIR if is_global else WORKSPACE_SKILLS_DIR
    scope = "Global" if is_global else "Workspace"
    print(f"\nInstalled Skills ({scope}): {target_base}")
    if not os.path.exists(target_base):
        print("  None installed yet.")
        return
    dirs = [d for d in os.listdir(target_base) if os.path.isdir(os.path.join(target_base, d))]
    print(f"Total installed: {len(dirs)}")
    for d in sorted(dirs):
        print(f"  ✓ {d}")
    print()

def print_help():
    print("""
Antigravity Skills Manager CLI:
  python skills-manager.py list                  - List all available skills
  python skills-manager.py search <term>         - Search skills by keyword
  python skills-manager.py install <id> [--global] - Install a skill
  python skills-manager.py bundle <name> [--global] - Install a bundle (core-dev, security-core, etc.)
  python skills-manager.py installed [--global]  - List currently installed skills
""")

def main():
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1].lower()
    is_global = "--global" in sys.argv

    if cmd == "list":
        filter_str = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else ""
        list_skills(filter_str)
    elif cmd == "search":
        term = sys.argv[2] if len(sys.argv) > 2 else ""
        search_skills(term)
    elif cmd == "install":
        if len(sys.argv) < 3:
            print("Usage: python skills-manager.py install <skill_id> [--global]")
            return
        skill_id = sys.argv[2]
        install_skill(skill_id, is_global)
    elif cmd == "bundle":
        if len(sys.argv) < 3:
            print("Usage: python skills-manager.py bundle <bundle_name> [--global]")
            return
        bundle_name = sys.argv[2]
        install_bundle(bundle_name, is_global)
    elif cmd == "installed":
        list_installed(is_global)
    else:
        print_help()

if __name__ == "__main__":
    main()

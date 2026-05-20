#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project cleanup script
Delete invalid and irrelevant process files and folders
"""

import os
import shutil
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def remove_item(path, description):
    if os.path.exists(path):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            print(f"REMOVED: {description} ({path})")
            return True
        except Exception as e:
            print(f"FAILED: {description} ({path}) - {e}")
            return False
    else:
        print(f"NOT EXISTS: {description} ({path})")
    return False

def main():
    print_section("NetOps Project Cleanup Tool")

    # Project root directory
    project_root = Path(__file__).parent

    # List of files and directories to remove
    items_to_remove = [
        # 1. Python cache files
        ("__pycache__", "Python cache directory"),
        ("src/__pycache__", "src cache directory"),
        ("src/core/__pycache__", "core cache directory"),
        ("src/ui/__pycache__", "ui cache directory"),
        ("src/ui/config_pages/__pycache__", "config_pages cache directory"),
        ("src/ui/config_pages/cisco/__pycache__", "cisco config cache directory"),
        ("src/ui/config_pages/h3c/__pycache__", "h3c config cache directory"),
        ("src/ui/config_pages/huawei/__pycache__", "huawei config cache directory"),
        ("src/ui/config_pages/ruijie/__pycache__", "ruijie config cache directory"),
        ("src/utils/__pycache__", "utils cache directory"),
        ("tests/__pycache__", "tests cache directory"),

        # 2. Build directory
        ("build", "PyInstaller build directory"),

        # 3. Log files
        ("logs", "Log directory"),

        # 4. Temporary files
        ("dist", "PyInstaller output directory (can be regenerated)"),
    ]

    total_removed = 0

    print_section("Starting cleanup")

    for pattern, description in items_to_remove:
        path = project_root / pattern

        # Handle wildcard patterns
        if '*' in pattern:
            # Find all matching files
            matched_files = list(project_root.glob(pattern))
            for file_path in matched_files:
                if remove_item(file_path, f"{description}"):
                    total_removed += 1
        else:
            # Directly remove specified path
            if remove_item(path, description):
                total_removed += 1

    print_section("Cleanup completed")
    print(f"Total removed: {total_removed} items")

    print_section("Project structure after cleanup")

    # Display cleaned project structure (only main directories)
    important_dirs = [
        "src",
        "src/core",
        "src/ui",
        "src/utils",
        "src/ui/config_pages",
        "scripts",
        "tests",
        "config",
        "output",
        "report",
    ]

    for dir_name in important_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            files = [f.name for f in dir_path.iterdir() if f.is_file() and f.suffix in ['.py', '.json', '.txt']]
            print(f"DIR {dir_name}: {len(files)} main files")

    print_section("Important notes")
    print("WARNING: The following files/directories need manual check:")
    print("   - dist/NetworkConfigGenerator.exe (if still needed)")
    print("   - config/ directory configuration files")
    print("   - output/ directory output files")
    print("   - projects_config.json (project configuration)")

    print("\nProject cleanup completed! Structure is now cleaner.")

if __name__ == "__main__":
    main()
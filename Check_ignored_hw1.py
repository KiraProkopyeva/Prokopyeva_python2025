import argparse
import os
import fnmatch
import re

def check_ignored_files(project_dir):
    gitignore_path = os.path.join(project_dir, ".gitignore")
    exact_rules = []
    pattern_rules = []

    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                rule = line.strip()
                if not rule or rule.startswith('#'):
                    continue
                normalized_rule = rule.replace(os.sep, '/')
                if normalized_rule.startswith('*.'):
                    pattern_rules.append(normalized_rule)
                else:
                    exact_rules.append(normalized_rule)
    else:
        print(f"Warning: file .gitignore is not found in {project_dir}")

    ignored_files_output = []

    normalized_project_dir = project_dir.rstrip('/\\')
    project_root_name = os.path.basename(normalized_project_dir)

    for root, dirs, files in os.walk(project_dir):
        if '.git' in dirs:
            dirs.remove('.git')

        for filename in files:
            if filename == ".gitignore":
                continue

            full_file_path = os.path.join(root, filename)
            relative_file_path = os.path.relpath(full_file_path, project_dir)
            relative_file_path_normalized = relative_file_path.replace(os.sep, '/')

            if project_root_name and project_root_name != '.':
                output_path = os.path.join(project_root_name, relative_file_path_normalized).replace(os.sep, '/')
            else:
                output_path = relative_file_path_normalized

            matched_rule_text = None

            for rule in exact_rules:
                if relative_file_path_normalized == rule:
                    matched_rule_text = rule
                    break

            if matched_rule_text:
                ignored_files_output.append(f"{output_path} ignored by expression {matched_rule_text}")
                continue

            for pattern_rule in pattern_rules:
                regex_equivalent = fnmatch.translate(pattern_rule)
                if re.match(regex_equivalent, filename):
                    matched_rule_text = pattern_rule
                    break

            if matched_rule_text:
                ignored_files_output.append(f"{output_path} ignored by expression {matched_rule_text}")

    if ignored_files_output:
        print("Ignored files:")
        for entry in ignored_files_output:
            print(entry)
    else:
        print("No files are ignored by .gitignore rules (or .gitignore is empty/missing).")

def main():
    parser = argparse.ArgumentParser(description="Check ignored files based on .gitignore")
    parser.add_argument("--project_dir", required=True, help="Path to the project directory")
    args = parser.parse_args()

    project_path = args.project_dir

    if not os.path.isdir(project_path):
        print(f"Error: directory '{project_path}' is not found.")
        return

    check_ignored_files(project_path)

if __name__ == "__main__":
    main()
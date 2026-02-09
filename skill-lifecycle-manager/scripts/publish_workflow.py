#!/usr/bin/env python3
"""
Skill Publishing Workflow
Handles the complete publishing process for skills including validation,
versioning, and release notes generation.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from lifecycle_manager import SkillLifecycleManager, SkillStatus


class PublishingWorkflow:
    """Manages the skill publishing workflow"""
    
    def __init__(self, skills_dir: str = "."):
        self.skills_dir = Path(skills_dir)
        self.manager = SkillLifecycleManager(skills_dir)
        self.workflow_state_file = self.skills_dir / ".publish-workflow.json"
        self.workflow_state = self._load_workflow_state()
    
    def _load_workflow_state(self) -> Dict:
        """Load publishing workflow state"""
        if self.workflow_state_file.exists():
            with open(self.workflow_state_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_workflow_state(self):
        """Save publishing workflow state"""
        with open(self.workflow_state_file, 'w') as f:
            json.dump(self.workflow_state, f, indent=2)
    
    def validate_skill_structure(self, skill_name: str) -> Tuple[bool, List[str]]:
        """Validate skill has proper structure"""
        errors = []
        skill_path = self.skills_dir / skill_name
        
        # Check required files
        required_files = ["SKILL.md"]
        for file in required_files:
            if not (skill_path / file).exists():
                errors.append(f"Missing required file: {file}")
        
        # Check SKILL.md structure
        skill_md = skill_path / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text()
            
            # Check frontmatter
            if not content.startswith("---"):
                errors.append("SKILL.md missing YAML frontmatter")
            
            # Check required sections
            required_sections = [
                ("name:", "Skill name in frontmatter"),
                ("description:", "Skill description in frontmatter"),
                ("#", "Main heading"),
                ("## When to Use", "When to use section"),
                ("## What This Skill Does", "What it does section"),
                ("## How to Use", "How to use section"),
            ]
            
            for pattern, desc in required_sections:
                if pattern not in content:
                    errors.append(f"Missing: {desc}")
        
        return len(errors) == 0, errors
    
    def run_pre_publish_checks(self, skill_name: str) -> Tuple[bool, List[str]]:
        """Run all pre-publish validation checks"""
        print(f"\n🔍 Running pre-publish checks for '{skill_name}'...")
        
        all_errors = []
        
        # Check 1: Structure validation
        print("  Checking skill structure...")
        valid, errors = self.validate_skill_structure(skill_name)
        if not valid:
            all_errors.extend(errors)
            print(f"  ✗ Structure check failed: {len(errors)} errors")
        else:
            print("  ✓ Structure check passed")
        
        # Check 2: Lifecycle validation
        print("  Checking lifecycle status...")
        skill = self.manager.get_skill_status(skill_name)
        if not skill:
            all_errors.append(f"Skill '{skill_name}' not initialized in lifecycle manager")
        elif skill.status not in [SkillStatus.BETA, SkillStatus.STABLE]:
            all_errors.append(f"Skill status is '{skill.status.value}', must be 'beta' or 'stable' to publish")
        else:
            print(f"  ✓ Lifecycle check passed (status: {skill.status.value})")
        
        # Check 3: Documentation completeness
        print("  Checking documentation...")
        valid, errors = self._check_documentation_completeness(skill_name)
        if not valid:
            all_errors.extend(errors)
            print(f"  ✗ Documentation check failed: {len(errors)} errors")
        else:
            print("  ✓ Documentation check passed")
        
        # Check 4: Examples validation
        print("  Checking examples...")
        valid, errors = self._check_examples(skill_name)
        if not valid:
            all_errors.extend(errors)
            print(f"  ✗ Examples check failed: {len(errors)} errors")
        else:
            print("  ✓ Examples check passed")
        
        return len(all_errors) == 0, all_errors
    
    def _check_documentation_completeness(self, skill_name: str) -> Tuple[bool, List[str]]:
        """Check if documentation is complete"""
        errors = []
        skill_md = self.skills_dir / skill_name / "SKILL.md"
        
        if not skill_md.exists():
            return False, ["SKILL.md not found"]
        
        content = skill_md.read_text()
        
        # Check for minimum content length
        if len(content) < 500:
            errors.append("Documentation too short (minimum 500 characters)")
        
        # Check for specific sections
        recommended_sections = [
            ("## Tips", "Tips section"),
            ("## Common Use Cases", "Common use cases section"),
        ]
        
        for pattern, desc in recommended_sections:
            if pattern not in content:
                errors.append(f"Recommended section missing: {desc}")
        
        return len(errors) == 0, errors
    
    def _check_examples(self, skill_name: str) -> Tuple[bool, List[str]]:
        """Check if examples are valid"""
        errors = []
        skill_md = self.skills_dir / skill_name / "SKILL.md"
        
        if not skill_md.exists():
            return False, ["SKILL.md not found"]
        
        content = skill_md.read_text()
        
        # Check for code blocks in examples
        example_section = re.search(r'## Example.*?(?=##|$)', content, re.DOTALL)
        if example_section:
            example_content = example_section.group(0)
            if '```' not in example_content:
                errors.append("Examples should include code blocks")
        
        return len(errors) == 0, errors
    
    def generate_release_notes(self, skill_name: str, version: str) -> str:
        """Generate release notes for a skill"""
        skill = self.manager.get_skill_status(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")
        
        skill_md = self.skills_dir / skill_name / "SKILL.md"
        content = skill_md.read_text() if skill_md.exists() else ""
        
        # Extract description from frontmatter or content
        description = skill.description
        
        release_notes = f"""# Release Notes: {skill_name} v{version}

**Release Date:** {datetime.now().strftime('%Y-%m-%d')}
**Status:** {skill.status.value}

## Description
{description}

## What's Included
- Complete SKILL.md documentation
- Usage examples and instructions
- Lifecycle status: {skill.status.value}

## Installation
```bash
# Copy skill to your skills directory
cp -r {skill_name} ~/.config/claude-code/skills/
```

## Usage
See [SKILL.md](./{skill_name}/SKILL.md) for detailed usage instructions.

## Changelog
"""
        
        # Add status history
        for transition in skill.status_history[-5:]:  # Last 5 transitions
            if transition.get('to'):
                release_notes += f"- {transition['date'][:10]}: Transitioned to {transition['to']}\n"
        
        return release_notes
    
    def publish_skill(self, skill_name: str, version: str, dry_run: bool = False) -> bool:
        """Execute the full publishing workflow"""
        print(f"\n📦 Publishing workflow for '{skill_name}' v{version}")
        print("=" * 60)
        
        # Step 1: Pre-publish checks
        valid, errors = self.run_pre_publish_checks(skill_name)
        if not valid:
            print("\n✗ Pre-publish checks failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        if dry_run:
            print("\n✓ Dry run complete - all checks passed")
            return True
        
        # Step 2: Update version
        print(f"\n📝 Updating version to {version}...")
        skill = self.manager.metadata[skill_name]
        skill.version = version
        skill.updated_at = datetime.now().isoformat()
        self.manager._save_metadata()
        print("  ✓ Version updated")
        
        # Step 3: Generate release notes
        print("\n📄 Generating release notes...")
        release_notes = self.generate_release_notes(skill_name, version)
        release_notes_path = self.skills_dir / skill_name / "RELEASE_NOTES.md"
        release_notes_path.write_text(release_notes)
        print(f"  ✓ Release notes saved to {release_notes_path}")
        
        # Step 4: Record publish event
        self.workflow_state[skill_name] = {
            "version": version,
            "published_at": datetime.now().isoformat(),
            "status": skill.status.value
        }
        self._save_workflow_state()
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully published '{skill_name}' v{version}")
        print("=" * 60)
        
        return True
    
    def get_publish_history(self, skill_name: Optional[str] = None) -> Dict:
        """Get publishing history"""
        if skill_name:
            return self.workflow_state.get(skill_name, {})
        return self.workflow_state


def main():
    """CLI for publishing workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Skill Publishing Workflow")
    parser.add_argument("--skills-dir", default=".", help="Skills directory")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Run pre-publish checks")
    check_parser.add_argument("skill", help="Skill name")
    
    # Publish command
    publish_parser = subparsers.add_parser("publish", help="Publish a skill")
    publish_parser.add_argument("skill", help="Skill name")
    publish_parser.add_argument("--version", required=True, help="Version number")
    publish_parser.add_argument("--dry-run", action="store_true", help="Run without making changes")
    
    # Release notes command
    notes_parser = subparsers.add_parser("notes", help="Generate release notes")
    notes_parser.add_argument("skill", help="Skill name")
    notes_parser.add_argument("--version", default="1.0.0", help="Version number")
    
    # History command
    history_parser = subparsers.add_parser("history", help="View publish history")
    history_parser.add_argument("--skill", help="Specific skill (default: all)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    workflow = PublishingWorkflow(args.skills_dir)
    
    if args.command == "check":
        valid, errors = workflow.run_pre_publish_checks(args.skill)
        if valid:
            print(f"\n✅ All checks passed for '{args.skill}'")
        else:
            print(f"\n❌ Checks failed for '{args.skill}':")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
    
    elif args.command == "publish":
        success = workflow.publish_skill(args.skill, args.version, args.dry_run)
        if not success:
            sys.exit(1)
    
    elif args.command == "notes":
        notes = workflow.generate_release_notes(args.skill, args.version)
        print(notes)
    
    elif args.command == "history":
        history = workflow.get_publish_history(args.skill)
        print(json.dumps(history, indent=2))


if __name__ == "__main__":
    main()

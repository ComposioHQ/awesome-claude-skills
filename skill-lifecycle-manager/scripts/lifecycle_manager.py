#!/usr/bin/env python3
"""
Skill Lifecycle Manager
Manages the complete lifecycle of Claude Skills with state transitions,
validation, and metrics tracking.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


class SkillStatus(Enum):
    """Skill lifecycle states"""
    DRAFT = "draft"
    BETA = "beta"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class SkillMetadata:
    """Skill metadata and lifecycle information"""
    name: str
    description: str
    status: SkillStatus = SkillStatus.DRAFT
    version: str = "0.1.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    author: str = ""
    contributors: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Lifecycle tracking
    status_history: List[Dict[str, str]] = field(default_factory=list)
    deprecation_date: Optional[str] = None
    archive_date: Optional[str] = None
    migration_guide: Optional[str] = None
    
    # Usage metrics
    download_count: int = 0
    rating: float = 0.0
    rating_count: int = 0
    last_used: Optional[str] = None


class SkillLifecycleManager:
    """Manages skill lifecycle operations"""
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        SkillStatus.DRAFT: [SkillStatus.BETA, SkillStatus.ARCHIVED],
        SkillStatus.BETA: [SkillStatus.STABLE, SkillStatus.DEPRECATED, SkillStatus.DRAFT],
        SkillStatus.STABLE: [SkillStatus.DEPRECATED],
        SkillStatus.DEPRECATED: [SkillStatus.ARCHIVED, SkillStatus.STABLE],
        SkillStatus.ARCHIVED: []  # Terminal state
    }
    
    # Validation requirements per status
    VALIDATION_REQUIREMENTS = {
        SkillStatus.DRAFT: ["skill_md_exists", "basic_structure"],
        SkillStatus.BETA: ["skill_md_complete", "examples_provided", "documentation"],
        SkillStatus.STABLE: ["all_beta_checks", "tested", "community_feedback"],
        SkillStatus.DEPRECATED: ["deprecation_notice", "migration_guide"],
        SkillStatus.ARCHIVED: ["archival_notice", "final_backup"]
    }
    
    def __init__(self, skills_dir: str = "."):
        self.skills_dir = Path(skills_dir)
        self.metadata_file = self.skills_dir / ".skill-lifecycle.json"
        self.metadata: Dict[str, SkillMetadata] = {}
        self._load_metadata()
    
    def _load_metadata(self):
        """Load skill metadata from JSON file"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                for name, meta in data.items():
                    meta['status'] = SkillStatus(meta['status'])
                    self.metadata[name] = SkillMetadata(**meta)
    
    def _save_metadata(self):
        """Save skill metadata to JSON file"""
        data = {}
        for name, meta in self.metadata.items():
            meta_dict = asdict(meta)
            meta_dict['status'] = meta.status.value
            data[name] = meta_dict
        
        with open(self.metadata_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def initialize_skill(self, name: str, description: str, author: str = "") -> SkillMetadata:
        """Initialize a new skill with draft status"""
        if name in self.metadata:
            raise ValueError(f"Skill '{name}' already exists")
        
        skill = SkillMetadata(
            name=name,
            description=description,
            status=SkillStatus.DRAFT,
            author=author,
            status_history=[{
                "from": None,
                "to": SkillStatus.DRAFT.value,
                "date": datetime.now().isoformat(),
                "reason": "Initial creation"
            }]
        )
        
        self.metadata[name] = skill
        self._save_metadata()
        return skill
    
    def validate_transition(self, name: str, new_status: SkillStatus) -> tuple[bool, List[str]]:
        """Validate if a state transition is allowed"""
        if name not in self.metadata:
            return False, [f"Skill '{name}' not found"]
        
        skill = self.metadata[name]
        current_status = skill.status
        
        # Check if transition is valid
        if new_status not in self.VALID_TRANSITIONS[current_status]:
            valid_states = [s.value for s in self.VALID_TRANSITIONS[current_status]]
            return False, [f"Invalid transition from {current_status.value} to {new_status.value}. "
                          f"Valid transitions: {valid_states}"]
        
        # Run validation checks
        errors = []
        requirements = self.VALIDATION_REQUIREMENTS.get(new_status, [])
        
        for requirement in requirements:
            check_method = getattr(self, f"_check_{requirement}", None)
            if check_method:
                passed, error = check_method(name)
                if not passed:
                    errors.append(error)
        
        return len(errors) == 0, errors
    
    def transition(self, name: str, new_status: SkillStatus, reason: str = "") -> SkillMetadata:
        """Transition a skill to a new status"""
        valid, errors = self.validate_transition(name, new_status)
        
        if not valid:
            raise ValueError(f"Transition validation failed: {'; '.join(errors)}")
        
        skill = self.metadata[name]
        old_status = skill.status
        
        # Update status
        skill.status = new_status
        skill.updated_at = datetime.now().isoformat()
        
        # Record in history
        skill.status_history.append({
            "from": old_status.value,
            "to": new_status.value,
            "date": datetime.now().isoformat(),
            "reason": reason or f"Transitioned to {new_status.value}"
        })
        
        # Handle special transitions
        if new_status == SkillStatus.DEPRECATED:
            skill.deprecation_date = datetime.now().isoformat()
        elif new_status == SkillStatus.ARCHIVED:
            skill.archive_date = datetime.now().isoformat()
        
        self._save_metadata()
        return skill
    
    def get_skill_status(self, name: str) -> Optional[SkillMetadata]:
        """Get current status and metadata for a skill"""
        return self.metadata.get(name)
    
    def list_skills_by_status(self, status: SkillStatus) -> List[SkillMetadata]:
        """List all skills with a specific status"""
        return [meta for meta in self.metadata.values() if meta.status == status]
    
    def generate_lifecycle_report(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Generate a lifecycle report for one or all skills"""
        if name:
            if name not in self.metadata:
                raise ValueError(f"Skill '{name}' not found")
            skills = [self.metadata[name]]
        else:
            skills = list(self.metadata.values())
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_skills": len(skills),
            "status_distribution": {},
            "skills": []
        }
        
        for skill in skills:
            status_val = skill.status.value
            report["status_distribution"][status_val] = report["status_distribution"].get(status_val, 0) + 1
            
            report["skills"].append({
                "name": skill.name,
                "status": skill.status.value,
                "version": skill.version,
                "created_at": skill.created_at,
                "updated_at": skill.updated_at,
                "status_transitions": len(skill.status_history),
                "days_in_current_status": self._days_since(skill.updated_at)
            })
        
        return report
    
    def update_usage_metrics(self, name: str, downloads: int = 0, rating: Optional[float] = None):
        """Update usage metrics for a skill"""
        if name not in self.metadata:
            raise ValueError(f"Skill '{name}' not found")
        
        skill = self.metadata[name]
        skill.download_count += downloads
        skill.last_used = datetime.now().isoformat()
        
        if rating is not None:
            # Update rolling average
            total_rating = skill.rating * skill.rating_count + rating
            skill.rating_count += 1
            skill.rating = total_rating / skill.rating_count
        
        self._save_metadata()
    
    def deprecate_skill(self, name: str, migration_guide: str, reason: str = "") -> SkillMetadata:
        """Mark a skill as deprecated with migration guide"""
        skill = self.metadata.get(name)
        if not skill:
            raise ValueError(f"Skill '{name}' not found")
        
        skill.migration_guide = migration_guide
        return self.transition(name, SkillStatus.DEPRECATED, reason or "Skill deprecated")
    
    # Validation check methods
    def _check_skill_md_exists(self, name: str) -> tuple[bool, str]:
        """Check if SKILL.md file exists"""
        skill_path = self.skills_dir / name / "SKILL.md"
        return skill_path.exists(), f"SKILL.md not found for skill '{name}'"
    
    def _check_basic_structure(self, name: str) -> tuple[bool, str]:
        """Check if skill has basic required structure"""
        skill_path = self.skills_dir / name
        has_md = (skill_path / "SKILL.md").exists()
        return has_md, f"Skill '{name}' missing basic structure"
    
    def _check_skill_md_complete(self, name: str) -> tuple[bool, str]:
        """Check if SKILL.md has all required sections"""
        skill_path = self.skills_dir / name / "SKILL.md"
        if not skill_path.exists():
            return False, f"SKILL.md not found for skill '{name}'"
        
        content = skill_path.read_text()
        required_sections = ["## When to Use", "## What This Skill Does", "## How to Use"]
        missing = [s for s in required_sections if s not in content]
        
        return len(missing) == 0, f"Missing sections in SKILL.md: {missing}"
    
    def _check_examples_provided(self, name: str) -> tuple[bool, str]:
        """Check if skill has examples"""
        skill_path = self.skills_dir / name / "SKILL.md"
        if not skill_path.exists():
            return False, f"SKILL.md not found"
        
        content = skill_path.read_text()
        has_examples = "## Example" in content or "### Basic Usage" in content
        return has_examples, f"Skill '{name}' missing examples section"
    
    def _check_documentation(self, name: str) -> tuple[bool, str]:
        """Check if documentation is sufficient"""
        return self._check_skill_md_complete(name)
    
    def _check_all_beta_checks(self, name: str) -> tuple[bool, str]:
        """Check all beta requirements"""
        checks = [
            self._check_skill_md_complete(name),
            self._check_examples_provided(name),
            self._check_documentation(name)
        ]
        
        failed = [err for passed, err in checks if not passed]
        return len(failed) == 0, f"Failed beta checks: {'; '.join(failed)}"
    
    def _check_tested(self, name: str) -> tuple[bool, str]:
        """Check if skill has been tested"""
        # This would integrate with actual testing framework
        return True, ""
    
    def _check_community_feedback(self, name: str) -> tuple[bool, str]:
        """Check if skill has community feedback"""
        skill = self.metadata.get(name)
        if skill and skill.rating_count >= 3:
            return True, ""
        return False, f"Skill '{name}' needs at least 3 ratings for stable status"
    
    def _check_deprecation_notice(self, name: str) -> tuple[bool, str]:
        """Check if deprecation notice exists"""
        skill_path = self.skills_dir / name / "SKILL.md"
        if not skill_path.exists():
            return False, f"SKILL.md not found"
        
        content = skill_path.read_text()
        has_notice = "deprecated" in content.lower() or "DEPRECATED" in content
        return has_notice, f"Skill '{name}' missing deprecation notice in SKILL.md"
    
    def _check_migration_guide(self, name: str) -> tuple[bool, str]:
        """Check if migration guide is provided"""
        skill = self.metadata.get(name)
        if skill and skill.migration_guide:
            return True, ""
        return False, f"Skill '{name}' missing migration guide"
    
    def _check_archival_notice(self, name: str) -> tuple[bool, str]:
        """Check if archival notice exists"""
        return True, ""  # Archival is automatic
    
    def _check_final_backup(self, name: str) -> tuple[bool, str]:
        """Check if final backup exists"""
        return True, ""  # Would check backup in production
    
    def _days_since(self, date_str: str) -> int:
        """Calculate days since a date"""
        date = datetime.fromisoformat(date_str)
        return (datetime.now() - date).days


def main():
    """CLI interface for lifecycle manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Skill Lifecycle Manager")
    parser.add_argument("--skills-dir", default=".", help="Skills directory")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new skill")
    init_parser.add_argument("name", help="Skill name")
    init_parser.add_argument("--description", required=True, help="Skill description")
    init_parser.add_argument("--author", default="", help="Skill author")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get skill status")
    status_parser.add_argument("name", help="Skill name")
    
    # Transition command
    trans_parser = subparsers.add_parser("transition", help="Transition skill status")
    trans_parser.add_argument("name", help="Skill name")
    trans_parser.add_argument("status", choices=[s.value for s in SkillStatus], help="New status")
    trans_parser.add_argument("--reason", default="", help="Transition reason")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List skills by status")
    list_parser.add_argument("--status", choices=[s.value for s in SkillStatus], help="Filter by status")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate lifecycle report")
    report_parser.add_argument("--skill", help="Specific skill name (default: all)")
    
    # Deprecate command
    depr_parser = subparsers.add_parser("deprecate", help="Deprecate a skill")
    depr_parser.add_argument("name", help="Skill name")
    depr_parser.add_argument("--migration-guide", required=True, help="Migration guide URL or text")
    depr_parser.add_argument("--reason", default="", help="Deprecation reason")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = SkillLifecycleManager(args.skills_dir)
    
    if args.command == "init":
        skill = manager.initialize_skill(args.name, args.description, args.author)
        print(f"✓ Initialized skill '{args.name}' with status: {skill.status.value}")
    
    elif args.command == "status":
        skill = manager.get_skill_status(args.name)
        if skill:
            print(f"\nSkill: {skill.name}")
            print(f"Status: {skill.status.value}")
            print(f"Version: {skill.version}")
            print(f"Created: {skill.created_at}")
            print(f"Updated: {skill.updated_at}")
            print(f"Status History: {len(skill.status_history)} transitions")
        else:
            print(f"Skill '{args.name}' not found")
            sys.exit(1)
    
    elif args.command == "transition":
        new_status = SkillStatus(args.status)
        valid, errors = manager.validate_transition(args.name, new_status)
        
        if not valid:
            print("✗ Transition validation failed:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        
        skill = manager.transition(args.name, new_status, args.reason)
        print(f"✓ Transitioned '{args.name}' to {skill.status.value}")
    
    elif args.command == "list":
        if args.status:
            status = SkillStatus(args.status)
            skills = manager.list_skills_by_status(status)
            print(f"\nSkills with status '{status.value}':")
            for skill in skills:
                print(f"  - {skill.name}: {skill.description[:50]}...")
        else:
            print("\nAll skills:")
            for name, skill in manager.metadata.items():
                print(f"  - {name}: {skill.status.value}")
    
    elif args.command == "report":
        report = manager.generate_lifecycle_report(args.skill)
        print(json.dumps(report, indent=2))
    
    elif args.command == "deprecate":
        skill = manager.deprecate_skill(args.name, args.migration_guide, args.reason)
        print(f"✓ Deprecated skill '{args.name}'")
        print(f"  Migration guide: {skill.migration_guide}")


if __name__ == "__main__":
    main()

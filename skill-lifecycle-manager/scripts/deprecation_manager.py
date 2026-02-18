#!/usr/bin/env python3
"""
Skill Deprecation Manager
Handles skill deprecation workflows including user notifications,
migration guides, and sunset timelines.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from lifecycle_manager import SkillLifecycleManager, SkillStatus


@dataclass
class DeprecationPlan:
    """Deprecation plan for a skill"""
    skill_name: str
    deprecation_date: str
    end_of_life_date: str
    migration_guide: str
    replacement_skill: Optional[str] = None
    notification_schedule: List[int] = None  # Days before EOL to notify
    
    def __post_init__(self):
        if self.notification_schedule is None:
            self.notification_schedule = [90, 60, 30, 14, 7, 1]


class DeprecationManager:
    """Manages skill deprecation workflows"""
    
    def __init__(self, skills_dir: str = "."):
        self.skills_dir = Path(skills_dir)
        self.manager = SkillLifecycleManager(skills_dir)
        self.deprecation_plans_file = self.skills_dir / ".deprecation-plans.json"
        self.deprecation_plans: Dict[str, DeprecationPlan] = {}
        self._load_plans()
    
    def _load_plans(self):
        """Load deprecation plans from file"""
        if self.deprecation_plans_file.exists():
            with open(self.deprecation_plans_file, 'r') as f:
                data = json.load(f)
                for name, plan_data in data.items():
                    self.deprecation_plans[name] = DeprecationPlan(**plan_data)
    
    def _save_plans(self):
        """Save deprecation plans to file"""
        data = {}
        for name, plan in self.deprecation_plans.items():
            data[name] = {
                "skill_name": plan.skill_name,
                "deprecation_date": plan.deprecation_date,
                "end_of_life_date": plan.end_of_life_date,
                "migration_guide": plan.migration_guide,
                "replacement_skill": plan.replacement_skill,
                "notification_schedule": plan.notification_schedule
            }
        
        with open(self.deprecation_plans_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_deprecation_plan(
        self,
        skill_name: str,
        migration_guide: str,
        months_until_eol: int = 6,
        replacement_skill: Optional[str] = None
    ) -> DeprecationPlan:
        """Create a deprecation plan for a skill"""
        if skill_name not in self.manager.metadata:
            raise ValueError(f"Skill '{skill_name}' not found")
        
        now = datetime.now()
        deprecation_date = now.isoformat()
        end_of_life_date = (now + timedelta(days=30*months_until_eol)).isoformat()
        
        plan = DeprecationPlan(
            skill_name=skill_name,
            deprecation_date=deprecation_date,
            end_of_life_date=end_of_life_date,
            migration_guide=migration_guide,
            replacement_skill=replacement_skill
        )
        
        self.deprecation_plans[skill_name] = plan
        self._save_plans()
        
        return plan
    
    def deprecate_skill(
        self,
        skill_name: str,
        migration_guide: str,
        reason: str = "",
        months_until_eol: int = 6,
        replacement_skill: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Execute full deprecation workflow"""
        print(f"\n⚠️  Deprecating skill '{skill_name}'...")
        
        # Step 1: Create deprecation plan
        print("  Creating deprecation plan...")
        plan = self.create_deprecation_plan(
            skill_name=skill_name,
            migration_guide=migration_guide,
            months_until_eol=months_until_eol,
            replacement_skill=replacement_skill
        )
        print(f"  ✓ EOL scheduled for {plan.end_of_life_date[:10]}")
        
        # Step 2: Update skill status
        print("  Updating skill status...")
        try:
            skill = self.manager.deprecate_skill(skill_name, migration_guide, reason)
            print(f"  ✓ Status updated to '{skill.status.value}'")
        except ValueError as e:
            return False, str(e)
        
        # Step 3: Update SKILL.md with deprecation notice
        print("  Adding deprecation notice to documentation...")
        self._add_deprecation_notice(skill_name, plan)
        print("  ✓ Documentation updated")
        
        # Step 4: Generate deprecation announcement
        print("  Generating deprecation announcement...")
        announcement = self._generate_deprecation_announcement(skill_name, plan, reason)
        announcement_path = self.skills_dir / skill_name / "DEPRECATION_NOTICE.md"
        announcement_path.write_text(announcement)
        print(f"  ✓ Announcement saved to {announcement_path}")
        
        print(f"\n✅ Skill '{skill_name}' successfully deprecated")
        print(f"   Migration guide: {migration_guide}")
        if replacement_skill:
            print(f"   Replacement: {replacement_skill}")
        
        return True, "Success"
    
    def _add_deprecation_notice(self, skill_name: str, plan: DeprecationPlan):
        """Add deprecation notice to SKILL.md"""
        skill_md = self.skills_dir / skill_name / "SKILL.md"
        
        if not skill_md.exists():
            return
        
        content = skill_md.read_text()
        
        # Create deprecation notice
        notice = f"""---
name: {skill_name}
description: [DEPRECATED] {self.manager.metadata[skill_name].description}
---

# ⚠️ DEPRECATED

**This skill is deprecated and will reach end-of-life on {plan.end_of_life_date[:10]}.**

Please migrate to an alternative solution. See the migration guide for details:
{plan.migration_guide}

---

"""
        
        # Insert after frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                new_content = f"---{parts[1]}---\n\n{notice}{parts[2]}"
                skill_md.write_text(new_content)
    
    def _generate_deprecation_announcement(
        self,
        skill_name: str,
        plan: DeprecationPlan,
        reason: str = ""
    ) -> str:
        """Generate deprecation announcement"""
        skill = self.manager.metadata.get(skill_name)
        
        announcement = f"""# Deprecation Notice: {skill_name}

**Deprecation Date:** {plan.deprecation_date[:10]}
**End of Life:** {plan.end_of_life_date[:10]}

## Summary

The `{skill_name}` skill is being deprecated.

{f"**Reason:** {reason}" if reason else ""}

## Migration Path

{plan.migration_guide}

{f"**Replacement:** Use `{plan.replacement_skill}` instead." if plan.replacement_skill else ""}

## Timeline

- **Now:** Skill enters deprecated status
- **{plan.end_of_life_date[:10]}:** End of life - skill will be archived

## Support

During the deprecation period:
- Critical bug fixes will be addressed
- No new features will be added
- Migration support is available

## Action Required

Please plan your migration before the end-of-life date to avoid disruption.
"""
        
        return announcement
    
    def check_upcoming_eol(self, days: int = 30) -> List[DeprecationPlan]:
        """Check for skills approaching end-of-life"""
        upcoming = []
        now = datetime.now()
        
        for plan in self.deprecation_plans.values():
            eol_date = datetime.fromisoformat(plan.end_of_life_date)
            days_until = (eol_date - now).days
            
            if 0 <= days_until <= days:
                upcoming.append(plan)
        
        return sorted(upcoming, key=lambda p: p.end_of_life_date)
    
    def get_deprecation_status(self, skill_name: str) -> Optional[Dict]:
        """Get deprecation status for a skill"""
        skill = self.manager.get_skill_status(skill_name)
        plan = self.deprecation_plans.get(skill_name)
        
        if not skill or skill.status != SkillStatus.DEPRECATED:
            return None
        
        now = datetime.now()
        eol_date = datetime.fromisoformat(plan.end_of_life_date) if plan else now
        days_until = (eol_date - now).days
        
        return {
            "skill_name": skill_name,
            "status": skill.status.value,
            "deprecation_date": plan.deprecation_date if plan else None,
            "end_of_life_date": plan.end_of_life_date if plan else None,
            "days_until_eol": max(0, days_until),
            "migration_guide": plan.migration_guide if plan else None,
            "replacement_skill": plan.replacement_skill if plan else None
        }
    
    def archive_deprecated_skill(self, skill_name: str) -> bool:
        """Archive a skill that has reached end-of-life"""
        plan = self.deprecation_plans.get(skill_name)
        
        if not plan:
            print(f"No deprecation plan found for '{skill_name}'")
            return False
        
        now = datetime.now()
        eol_date = datetime.fromisoformat(plan.end_of_life_date)
        
        if now < eol_date:
            days_remaining = (eol_date - now).days
            print(f"Cannot archive yet. {days_remaining} days until EOL.")
            return False
        
        # Transition to archived
        try:
            self.manager.transition(skill_name, SkillStatus.ARCHIVED, "End of life reached")
            print(f"✅ Skill '{skill_name}' archived")
            return True
        except ValueError as e:
            print(f"❌ Failed to archive: {e}")
            return False


def main():
    """CLI for deprecation manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Skill Deprecation Manager")
    parser.add_argument("--skills-dir", default=".", help="Skills directory")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Deprecate command
    depr_parser = subparsers.add_parser("deprecate", help="Deprecate a skill")
    depr_parser.add_argument("skill", help="Skill name")
    depr_parser.add_argument("--migration-guide", required=True, help="Migration guide URL/path")
    depr_parser.add_argument("--reason", default="", help="Deprecation reason")
    depr_parser.add_argument("--months-until-eol", type=int, default=6, help="Months until EOL")
    depr_parser.add_argument("--replacement", help="Replacement skill name")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check deprecation status")
    status_parser.add_argument("skill", help="Skill name")
    
    # Check EOL command
    eol_parser = subparsers.add_parser("eol-check", help="Check upcoming EOLs")
    eol_parser.add_argument("--days", type=int, default=30, help="Days to check")
    
    # Archive command
    archive_parser = subparsers.add_parser("archive", help="Archive skill at EOL")
    archive_parser.add_argument("skill", help="Skill name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = DeprecationManager(args.skills_dir)
    
    if args.command == "deprecate":
        success, msg = manager.deprecate_skill(
            args.skill,
            args.migration_guide,
            args.reason,
            args.months_until_eol,
            args.replacement
        )
        if not success:
            print(f"Error: {msg}")
    
    elif args.command == "status":
        status = manager.get_deprecation_status(args.skill)
        if status:
            print(json.dumps(status, indent=2))
        else:
            print(f"Skill '{args.skill}' is not deprecated")
    
    elif args.command == "eol-check":
        upcoming = manager.check_upcoming_eol(args.days)
        if upcoming:
            print(f"\n⚠️  Skills approaching EOL (within {args.days} days):\n")
            for plan in upcoming:
                eol = datetime.fromisoformat(plan.end_of_life_date)
                days = (eol - datetime.now()).days
                print(f"  - {plan.skill_name}: {plan.end_of_life_date[:10]} ({days} days)")
        else:
            print(f"\n✅ No skills approaching EOL in the next {args.days} days")
    
    elif args.command == "archive":
        manager.archive_deprecated_skill(args.skill)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Skill Lifecycle Manager CLI (skillctl)
Unified command-line interface for managing skill lifecycles.
"""

import argparse
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lifecycle_manager import SkillLifecycleManager, SkillStatus, main as lifecycle_main
from publish_workflow import PublishingWorkflow, main as publish_main
from deprecation_manager import DeprecationManager, main as deprecation_main
from metrics_tracker import MetricsTracker, main as metrics_main
from report_generator import LifecycleReportGenerator, main as report_main


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Skill Lifecycle Manager - Unified CLI for skill management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  skillctl lifecycle init my-skill --description "My new skill"
  skillctl publish check my-skill
  skillctl publish my-skill --version 1.0.0
  skillctl deprecate my-skill --migration-guide "path/to/guide.md"
  skillctl metrics report --days 30
  skillctl report full --output report.md
        """
    )
    
    parser.add_argument("--skills-dir", default=".", help="Skills directory")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    subparsers = parser.add_subparsers(dest="command", help="Command category")
    
    # Lifecycle commands
    lifecycle_parser = subparsers.add_parser("lifecycle", help="Lifecycle management commands")
    lifecycle_sub = lifecycle_parser.add_subparsers(dest="lifecycle_cmd")
    
    lifecycle_init = lifecycle_sub.add_parser("init", help="Initialize a new skill")
    lifecycle_init.add_argument("name", help="Skill name")
    lifecycle_init.add_argument("--description", required=True)
    lifecycle_init.add_argument("--author", default="")
    
    lifecycle_status = lifecycle_sub.add_parser("status", help="Get skill status")
    lifecycle_status.add_argument("name", help="Skill name")
    
    lifecycle_transition = lifecycle_sub.add_parser("transition", help="Transition skill status")
    lifecycle_transition.add_argument("name", help="Skill name")
    lifecycle_transition.add_argument("status", choices=[s.value for s in SkillStatus])
    lifecycle_transition.add_argument("--reason", default="")
    
    lifecycle_list = lifecycle_sub.add_parser("list", help="List skills")
    lifecycle_list.add_argument("--status", choices=[s.value for s in SkillStatus])
    
    # Publish commands
    publish_parser = subparsers.add_parser("publish", help="Publishing workflow commands")
    publish_sub = publish_parser.add_subparsers(dest="publish_cmd")
    
    publish_check = publish_sub.add_parser("check", help="Run pre-publish checks")
    publish_check.add_argument("skill", help="Skill name")
    
    publish_cmd = publish_sub.add_parser("publish", help="Publish a skill")
    publish_cmd.add_argument("skill", help="Skill name")
    publish_cmd.add_argument("--version", required=True)
    publish_cmd.add_argument("--dry-run", action="store_true")
    
    publish_notes = publish_sub.add_parser("notes", help="Generate release notes")
    publish_notes.add_argument("skill", help="Skill name")
    publish_notes.add_argument("--version", default="1.0.0")
    
    # Deprecate commands
    deprecate_parser = subparsers.add_parser("deprecate", help="Deprecation management")
    deprecate_sub = deprecate_parser.add_subparsers(dest="deprecate_cmd")
    
    deprecate_cmd = deprecate_sub.add_parser("deprecate", help="Deprecate a skill")
    deprecate_cmd.add_argument("skill", help="Skill name")
    deprecate_cmd.add_argument("--migration-guide", required=True)
    deprecate_cmd.add_argument("--reason", default="")
    deprecate_cmd.add_argument("--months-until-eol", type=int, default=6)
    deprecate_cmd.add_argument("--replacement")
    
    deprecate_status = deprecate_sub.add_parser("status", help="Check deprecation status")
    deprecate_status.add_argument("skill", help="Skill name")
    
    deprecate_eol = deprecate_sub.add_parser("eol-check", help="Check upcoming EOLs")
    deprecate_eol.add_argument("--days", type=int, default=30)
    
    # Metrics commands
    metrics_parser = subparsers.add_parser("metrics", help="Usage metrics commands")
    metrics_sub = metrics_parser.add_subparsers(dest="metrics_cmd")
    
    metrics_record = metrics_sub.add_parser("record", help="Record usage event")
    metrics_record.add_argument("skill", help="Skill name")
    metrics_record.add_argument("--type", default="invoke", choices=["invoke", "complete", "error"])
    metrics_record.add_argument("--user")
    metrics_record.add_argument("--duration", type=int)
    
    metrics_report = metrics_sub.add_parser("report", help="Generate metrics report")
    metrics_report.add_argument("--skill")
    metrics_report.add_argument("--days", type=int, default=30)
    
    metrics_trending = metrics_sub.add_parser("trending", help="Get trending skills")
    metrics_trending.add_argument("--days", type=int, default=7)
    metrics_trending.add_argument("--limit", type=int, default=10)
    
    # Report commands
    report_parser = subparsers.add_parser("report", help="Lifecycle report commands")
    report_sub = report_parser.add_subparsers(dest="report_cmd")
    
    report_full = report_sub.add_parser("full", help="Generate full report")
    report_full.add_argument("--output", "-o")
    report_full.add_argument("--format", choices=["markdown", "json"], default="markdown")
    
    report_summary = report_sub.add_parser("summary", help="Generate summary")
    
    report_health = report_sub.add_parser("health", help="Get health metrics")
    
    report_recommendations = report_sub.add_parser("recommendations", help="Get recommendations")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute commands
    if args.command == "lifecycle":
        if not args.lifecycle_cmd:
            lifecycle_parser.print_help()
            sys.exit(1)
        
        manager = SkillLifecycleManager(args.skills_dir)
        
        if args.lifecycle_cmd == "init":
            skill = manager.initialize_skill(args.name, args.description, args.author)
            print(f"✓ Initialized skill '{args.name}' with status: {skill.status.value}")
        
        elif args.lifecycle_cmd == "status":
            skill = manager.get_skill_status(args.name)
            if skill:
                print(f"\nSkill: {skill.name}")
                print(f"Status: {skill.status.value}")
                print(f"Version: {skill.version}")
                print(f"Created: {skill.created_at}")
                print(f"Updated: {skill.updated_at}")
                print(f"Transitions: {len(skill.status_history)}")
            else:
                print(f"Skill '{args.name}' not found")
                sys.exit(1)
        
        elif args.lifecycle_cmd == "transition":
            new_status = SkillStatus(args.status)
            valid, errors = manager.validate_transition(args.name, new_status)
            
            if not valid:
                print("✗ Validation failed:")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)
            
            skill = manager.transition(args.name, new_status, args.reason)
            print(f"✓ Transitioned '{args.name}' to {skill.status.value}")
        
        elif args.lifecycle_cmd == "list":
            if args.status:
                status = SkillStatus(args.status)
                skills = manager.list_skills_by_status(status)
                print(f"\nSkills with status '{status.value}':")
                for skill in skills:
                    print(f"  - {skill.name}")
            else:
                print("\nAll skills:")
                for name, skill in manager.metadata.items():
                    print(f"  - {name}: {skill.status.value}")
    
    elif args.command == "publish":
        if not args.publish_cmd:
            publish_parser.print_help()
            sys.exit(1)
        
        workflow = PublishingWorkflow(args.skills_dir)
        
        if args.publish_cmd == "check":
            valid, errors = workflow.run_pre_publish_checks(args.skill)
            if valid:
                print(f"✅ All checks passed for '{args.skill}'")
            else:
                print(f"❌ Checks failed:")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)
        
        elif args.publish_cmd == "publish":
            success = workflow.publish_skill(args.skill, args.version, args.dry_run)
            if not success:
                sys.exit(1)
        
        elif args.publish_cmd == "notes":
            notes = workflow.generate_release_notes(args.skill, args.version)
            print(notes)
    
    elif args.command == "deprecate":
        if not args.deprecate_cmd:
            deprecate_parser.print_help()
            sys.exit(1)
        
        manager = DeprecationManager(args.skills_dir)
        
        if args.deprecate_cmd == "deprecate":
            success, msg = manager.deprecate_skill(
                args.skill,
                args.migration_guide,
                args.reason,
                args.months_until_eol,
                args.replacement
            )
            if not success:
                print(f"Error: {msg}")
                sys.exit(1)
        
        elif args.deprecate_cmd == "status":
            status = manager.get_deprecation_status(args.skill)
            if status:
                import json
                print(json.dumps(status, indent=2))
            else:
                print(f"Skill '{args.skill}' is not deprecated")
        
        elif args.deprecate_cmd == "eol-check":
            upcoming = manager.check_upcoming_eol(args.days)
            if upcoming:
                print(f"\n⚠️  Skills approaching EOL (within {args.days} days):\n")
                for plan in upcoming:
                    from datetime import datetime
                    eol = datetime.fromisoformat(plan.end_of_life_date)
                    days = (eol - datetime.now()).days
                    print(f"  - {plan.skill_name}: {plan.end_of_life_date[:10]} ({days} days)")
            else:
                print(f"\n✅ No skills approaching EOL in the next {args.days} days")
    
    elif args.command == "metrics":
        if not args.metrics_cmd:
            metrics_parser.print_help()
            sys.exit(1)
        
        tracker = MetricsTracker()
        
        if args.metrics_cmd == "record":
            tracker.record_event(args.skill, args.type, args.user, args.duration)
            print(f"✓ Recorded {args.type} for '{args.skill}'")
        
        elif args.metrics_cmd == "report":
            report = tracker.generate_report(args.skill, args.days)
            print(report)
        
        elif args.metrics_cmd == "trending":
            import json
            trending = tracker.get_trending_skills(args.days, args.limit)
            print(json.dumps(trending, indent=2))
    
    elif args.command == "report":
        if not args.report_cmd:
            report_parser.print_help()
            sys.exit(1)
        
        generator = LifecycleReportGenerator(args.skills_dir)
        
        if args.report_cmd == "full":
            if args.format == "markdown":
                output = generator.export_markdown_report(args.output)
            else:
                output = generator.export_json_report(args.output)
            
            if not args.output:
                print(output)
            else:
                print(f"✓ Report saved to {args.output}")
        
        elif args.report_cmd == "summary":
            import json
            report = generator.generate_full_report()
            print(json.dumps(report['summary'], indent=2))
        
        elif args.report_cmd == "health":
            import json
            report = generator.generate_full_report()
            print(json.dumps(report['health_metrics'], indent=2))
        
        elif args.report_cmd == "recommendations":
            report = generator.generate_full_report()
            for rec in report['recommendations']:
                print(f"[{rec['priority'].upper()}] {rec['skill']}: {rec['action']}")


if __name__ == "__main__":
    main()

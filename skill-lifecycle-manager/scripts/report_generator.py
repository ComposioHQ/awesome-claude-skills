#!/usr/bin/env python3
"""
Skill Lifecycle Report Generator
Generates comprehensive reports on skill lifecycles, transitions, and health.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

from lifecycle_manager import SkillLifecycleManager, SkillStatus


class LifecycleReportGenerator:
    """Generates comprehensive lifecycle reports"""
    
    def __init__(self, skills_dir: str = "."):
        self.skills_dir = Path(skills_dir)
        self.manager = SkillLifecycleManager(skills_dir)
    
    def generate_full_report(self) -> Dict[str, Any]:
        """Generate a comprehensive lifecycle report for all skills"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": self._generate_summary(),
            "status_breakdown": self._generate_status_breakdown(),
            "transition_analysis": self._analyze_transitions(),
            "health_metrics": self._calculate_health_metrics(),
            "recommendations": self._generate_recommendations(),
            "skills": []
        }
        
        # Add detailed info for each skill
        for name, meta in self.manager.metadata.items():
            report["skills"].append(self._generate_skill_report(name, meta))
        
        # Sort skills by status and name
        status_order = {s: i for i, s in enumerate([
            SkillStatus.DRAFT, SkillStatus.BETA, 
            SkillStatus.STABLE, SkillStatus.DEPRECATED, SkillStatus.ARCHIVED
        ])}
        report["skills"].sort(key=lambda x: (status_order.get(SkillStatus(x["status"]), 99), x["name"]))
        
        return report
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall summary statistics"""
        total = len(self.manager.metadata)
        
        status_counts = {status.value: 0 for status in SkillStatus}
        for meta in self.manager.metadata.values():
            status_counts[meta.status.value] += 1
        
        # Calculate average time in current status
        avg_days_in_status = []
        for meta in self.manager.metadata.values():
            days = self.manager._days_since(meta.updated_at)
            avg_days_in_status.append(days)
        
        return {
            "total_skills": total,
            "status_counts": status_counts,
            "average_days_in_current_status": sum(avg_days_in_status) / max(len(avg_days_in_status), 1),
            "recently_updated": sum(1 for m in self.manager.metadata.values() 
                                   if self.manager._days_since(m.updated_at) <= 30)
        }
    
    def _generate_status_breakdown(self) -> Dict[str, List[Dict]]:
        """Generate breakdown of skills by status"""
        breakdown = {status.value: [] for status in SkillStatus}
        
        for name, meta in self.manager.metadata.items():
            info = {
                "name": name,
                "version": meta.version,
                "created_at": meta.created_at,
                "updated_at": meta.updated_at,
                "days_in_status": self.manager._days_since(meta.updated_at)
            }
            breakdown[meta.status.value].append(info)
        
        return breakdown
    
    def _analyze_transitions(self) -> Dict[str, Any]:
        """Analyze status transitions"""
        transitions = []
        
        for name, meta in self.manager.metadata.items():
            for transition in meta.status_history:
                if transition.get("from") and transition.get("to"):
                    transitions.append({
                        "skill": name,
                        "from": transition["from"],
                        "to": transition["to"],
                        "date": transition["date"]
                    })
        
        # Count transitions by type
        transition_counts = {}
        for t in transitions:
            key = f"{t['from']} -> {t['to']}"
            transition_counts[key] = transition_counts.get(key, 0) + 1
        
        # Recent transitions (last 30 days)
        cutoff = datetime.now() - timedelta(days=30)
        recent = [t for t in transitions if datetime.fromisoformat(t["date"]) >= cutoff]
        
        return {
            "total_transitions": len(transitions),
            "transition_counts": transition_counts,
            "recent_transitions": len(recent),
            "recent_details": recent[:10]  # Last 10
        }
    
    def _calculate_health_metrics(self) -> Dict[str, Any]:
        """Calculate health metrics for the skill portfolio"""
        now = datetime.now()
        
        # Skills needing attention
        stale_threshold = 90  # days
        stale_skills = []
        
        for name, meta in self.manager.metadata.items():
            days_since_update = (now - datetime.fromisoformat(meta.updated_at)).days
            
            if meta.status == SkillStatus.DRAFT and days_since_update > stale_threshold:
                stale_skills.append({
                    "name": name,
                    "issue": "Draft for over 90 days",
                    "days": days_since_update
                })
            elif meta.status == SkillStatus.BETA and days_since_update > 60:
                stale_skills.append({
                    "name": name,
                    "issue": "In beta for over 60 days",
                    "days": days_since_update
                })
        
        # Calculate maturity ratio
        stable_count = sum(1 for m in self.manager.metadata.values() if m.status == SkillStatus.STABLE)
        total_active = sum(1 for m in self.manager.metadata.values() 
                         if m.status in [SkillStatus.DRAFT, SkillStatus.BETA, SkillStatus.STABLE])
        
        return {
            "stale_skills": stale_skills,
            "stale_count": len(stale_skills),
            "maturity_ratio": stable_count / max(total_active, 1),
            "health_score": max(0, 100 - len(stale_skills) * 5)  # Simple scoring
        }
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        for name, meta in self.manager.metadata.items():
            days_in_status = self.manager._days_since(meta.updated_at)
            
            if meta.status == SkillStatus.DRAFT:
                if days_in_status > 30:
                    recommendations.append({
                        "skill": name,
                        "priority": "medium",
                        "action": "Consider moving to beta",
                        "reason": f"In draft for {days_in_status} days"
                    })
            
            elif meta.status == SkillStatus.BETA:
                if days_in_status > 30:
                    recommendations.append({
                        "skill": name,
                        "priority": "high",
                        "action": "Evaluate for stable release",
                        "reason": f"Sufficient time in beta ({days_in_status} days)"
                    })
            
            elif meta.status == SkillStatus.DEPRECATED:
                if meta.deprecation_date:
                    eol_date = datetime.fromisoformat(meta.deprecation_date) + timedelta(days=180)
                    days_to_eol = (eol_date - datetime.now()).days
                    
                    if days_to_eol <= 30:
                        recommendations.append({
                            "skill": name,
                            "priority": "urgent",
                            "action": "Prepare for archival",
                            "reason": f"EOL in {days_to_eol} days"
                        })
        
        # Sort by priority
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 99))
        
        return recommendations
    
    def _generate_skill_report(self, name: str, meta) -> Dict[str, Any]:
        """Generate detailed report for a single skill"""
        days_in_status = self.manager._days_since(meta.updated_at)
        
        return {
            "name": name,
            "status": meta.status.value,
            "version": meta.version,
            "description": meta.description,
            "author": meta.author,
            "created_at": meta.created_at,
            "updated_at": meta.updated_at,
            "days_in_current_status": days_in_status,
            "status_transitions": len(meta.status_history),
            "history": meta.status_history,
            "deprecation_info": {
                "date": meta.deprecation_date,
                "migration_guide": meta.migration_guide
            } if meta.status == SkillStatus.DEPRECATED else None,
            "archive_info": {
                "date": meta.archive_date
            } if meta.status == SkillStatus.ARCHIVED else None
        }
    
    def export_markdown_report(self, output_file: Optional[str] = None) -> str:
        """Export report as Markdown"""
        report = self.generate_full_report()
        
        lines = [
            "# Skill Lifecycle Report",
            f"\n**Generated:** {report['generated_at'][:10]}",
            "",
            "## Summary",
            f"- **Total Skills:** {report['summary']['total_skills']}",
            f"- **Recently Updated:** {report['summary']['recently_updated']}",
            f"- **Avg Days in Status:** {report['summary']['average_days_in_current_status']:.1f}",
            f"- **Health Score:** {report['health_metrics']['health_score']}/100",
            "",
            "## Status Distribution",
            ""
        ]
        
        for status, count in report['summary']['status_counts'].items():
            lines.append(f"- **{status.title()}:** {count}")
        
        # Recommendations
        if report['recommendations']:
            lines.extend([
                "",
                "## Recommendations",
                ""
            ])
            for rec in report['recommendations'][:10]:
                emoji = {"urgent": "🔴", "high": "🟡", "medium": "🟢"}.get(rec['priority'], "⚪")
                lines.append(f"{emoji} **{rec['skill']}** ({rec['priority']})")
                lines.append(f"   - Action: {rec['action']}")
                lines.append(f"   - Reason: {rec['reason']}")
                lines.append("")
        
        # Stale skills
        if report['health_metrics']['stale_skills']:
            lines.extend([
                "## Skills Needing Attention",
                ""
            ])
            for skill in report['health_metrics']['stale_skills'][:5]:
                lines.append(f"- **{skill['name']}**: {skill['issue']} ({skill['days']} days)")
        
        # Detailed skill list
        lines.extend([
            "",
            "## Skill Details",
            ""
        ])
        
        for skill in report['skills']:
            status_emoji = {
                "draft": "📝",
                "beta": "🧪",
                "stable": "✅",
                "deprecated": "⚠️",
                "archived": "📦"
            }.get(skill['status'], "❓")
            
            lines.append(f"### {status_emoji} {skill['name']} ({skill['status']})")
            lines.append(f"- Version: {skill['version']}")
            lines.append(f"- Created: {skill['created_at'][:10]}")
            lines.append(f"- Days in status: {skill['days_in_current_status']}")
            if skill['status_transitions'] > 0:
                lines.append(f"- Transitions: {skill['status_transitions']}")
            lines.append("")
        
        markdown = '\n'.join(lines)
        
        if output_file:
            Path(output_file).write_text(markdown)
        
        return markdown
    
    def export_json_report(self, output_file: Optional[str] = None) -> str:
        """Export report as JSON"""
        report = self.generate_full_report()
        json_str = json.dumps(report, indent=2)
        
        if output_file:
            Path(output_file).write_text(json_str)
        
        return json_str


def main():
    """CLI for report generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Skill Lifecycle Report Generator")
    parser.add_argument("--skills-dir", default=".", help="Skills directory")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Full report command
    subparsers.add_parser("full", help="Generate full lifecycle report")
    
    # Summary command
    subparsers.add_parser("summary", help="Generate summary only")
    
    # Recommendations command
    subparsers.add_parser("recommendations", help="Get recommendations")
    
    # Health command
    subparsers.add_parser("health", help="Get health metrics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    generator = LifecycleReportGenerator(args.skills_dir)
    
    if args.command == "full":
        if args.format == "markdown":
            output = generator.export_markdown_report(args.output)
        else:
            output = generator.export_json_report(args.output)
        
        if not args.output:
            print(output)
        else:
            print(f"✓ Report saved to {args.output}")
    
    elif args.command == "summary":
        report = generator.generate_full_report()
        print(json.dumps(report['summary'], indent=2))
    
    elif args.command == "recommendations":
        report = generator.generate_full_report()
        for rec in report['recommendations']:
            print(f"[{rec['priority'].upper()}] {rec['skill']}: {rec['action']}")
    
    elif args.command == "health":
        report = generator.generate_full_report()
        print(json.dumps(report['health_metrics'], indent=2))


if __name__ == "__main__":
    main()

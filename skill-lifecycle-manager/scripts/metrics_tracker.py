#!/usr/bin/env python3
"""
Skill Usage Metrics Tracker
Tracks and analyzes skill usage patterns, adoption rates, and performance metrics.
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class UsageEvent:
    """A single usage event"""
    timestamp: str
    skill_name: str
    event_type: str  # 'invoke', 'complete', 'error'
    user_id: Optional[str] = None
    duration_ms: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillMetrics:
    """Aggregated metrics for a skill"""
    skill_name: str
    total_invocations: int = 0
    successful_completions: int = 0
    errors: int = 0
    unique_users: int = 0
    avg_duration_ms: float = 0.0
    first_used: Optional[str] = None
    last_used: Optional[str] = None
    daily_usage: Dict[str, int] = field(default_factory=dict)
    hourly_distribution: List[int] = field(default_factory=lambda: [0]*24)
    user_ids: set = field(default_factory=set)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "skill_name": self.skill_name,
            "total_invocations": self.total_invocations,
            "successful_completions": self.successful_completions,
            "errors": self.errors,
            "unique_users": len(self.user_ids),
            "avg_duration_ms": self.avg_duration_ms,
            "first_used": self.first_used,
            "last_used": self.last_used,
            "daily_usage": self.daily_usage,
            "hourly_distribution": self.hourly_distribution
        }


class MetricsTracker:
    """Tracks and analyzes skill usage metrics"""
    
    def __init__(self, data_dir: str = ".metrics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.events_file = self.data_dir / "usage_events.jsonl"
        self.metrics_file = self.data_dir / "aggregated_metrics.json"
        
        self.metrics: Dict[str, SkillMetrics] = {}
        self._load_metrics()
    
    def _load_metrics(self):
        """Load aggregated metrics from file"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
                for skill_name, metrics_data in data.items():
                    metrics = SkillMetrics(skill_name=skill_name)
                    for key, value in metrics_data.items():
                        if hasattr(metrics, key):
                            setattr(metrics, key, value)
                    self.metrics[skill_name] = metrics
    
    def _save_metrics(self):
        """Save aggregated metrics to file"""
        data = {name: metrics.to_dict() for name, metrics in self.metrics.items()}
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_event(
        self,
        skill_name: str,
        event_type: str,
        user_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
        context: Optional[Dict] = None
    ):
        """Record a usage event"""
        event = UsageEvent(
            timestamp=datetime.now().isoformat(),
            skill_name=skill_name,
            event_type=event_type,
            user_id=user_id,
            duration_ms=duration_ms,
            context=context or {}
        )
        
        # Append to events file
        with open(self.events_file, 'a') as f:
            f.write(json.dumps(asdict(event)) + '\n')
        
        # Update aggregated metrics
        self._update_metrics(event)
    
    def _update_metrics(self, event: UsageEvent):
        """Update aggregated metrics from an event"""
        if event.skill_name not in self.metrics:
            self.metrics[event.skill_name] = SkillMetrics(skill_name=event.skill_name)
        
        metrics = self.metrics[event.skill_name]
        timestamp = datetime.fromisoformat(event.timestamp)
        date_str = timestamp.strftime('%Y-%m-%d')
        hour = timestamp.hour
        
        # Update basic counters
        if event.event_type == 'invoke':
            metrics.total_invocations += 1
            metrics.daily_usage[date_str] = metrics.daily_usage.get(date_str, 0) + 1
            metrics.hourly_distribution[hour] += 1
            
            if metrics.first_used is None:
                metrics.first_used = event.timestamp
            metrics.last_used = event.timestamp
        
        elif event.event_type == 'complete':
            metrics.successful_completions += 1
            
            # Update average duration
            if event.duration_ms:
                total_duration = metrics.avg_duration_ms * (metrics.successful_completions - 1)
                metrics.avg_duration_ms = (total_duration + event.duration_ms) / metrics.successful_completions
        
        elif event.event_type == 'error':
            metrics.errors += 1
        
        # Track unique users
        if event.user_id:
            metrics.user_ids.add(event.user_id)
        
        self._save_metrics()
    
    def get_metrics(self, skill_name: str) -> Optional[SkillMetrics]:
        """Get metrics for a specific skill"""
        return self.metrics.get(skill_name)
    
    def get_all_metrics(self) -> Dict[str, SkillMetrics]:
        """Get metrics for all skills"""
        return self.metrics
    
    def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get usage summary for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        summary = {
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "total_skills": len(self.metrics),
            "total_invocations": 0,
            "total_unique_users": set(),
            "skill_summaries": []
        }
        
        for skill_name, metrics in self.metrics.items():
            # Filter to period
            period_invocations = sum(
                count for date, count in metrics.daily_usage.items()
                if datetime.fromisoformat(date) >= cutoff_date
            )
            
            if period_invocations > 0:
                skill_summary = {
                    "skill_name": skill_name,
                    "invocations": period_invocations,
                    "success_rate": metrics.successful_completions / max(metrics.total_invocations, 1),
                    "unique_users": len(metrics.user_ids),
                    "avg_duration_ms": metrics.avg_duration_ms
                }
                summary["skill_summaries"].append(skill_summary)
                summary["total_invocations"] += period_invocations
                summary["total_unique_users"].update(metrics.user_ids)
        
        summary["total_unique_users"] = len(summary["total_unique_users"])
        summary["skill_summaries"].sort(key=lambda x: x["invocations"], reverse=True)
        
        return summary
    
    def get_trending_skills(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get trending skills based on recent usage"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        trending = []
        for skill_name, metrics in self.metrics.items():
            recent_usage = sum(
                count for date, count in metrics.daily_usage.items()
                if datetime.fromisoformat(date) >= cutoff_date
            )
            
            if recent_usage > 0:
                trending.append({
                    "skill_name": skill_name,
                    "recent_invocations": recent_usage,
                    "total_invocations": metrics.total_invocations,
                    "unique_users": len(metrics.user_ids)
                })
        
        trending.sort(key=lambda x: x["recent_invocations"], reverse=True)
        return trending[:limit]
    
    def get_adoption_funnel(self, skill_name: str) -> Dict[str, Any]:
        """Analyze adoption funnel for a skill"""
        metrics = self.metrics.get(skill_name)
        if not metrics:
            return {}
        
        total = metrics.total_invocations
        if total == 0:
            return {"error": "No usage data"}
        
        return {
            "skill_name": skill_name,
            "total_invocations": total,
            "successful_completions": metrics.successful_completions,
            "completion_rate": metrics.successful_completions / total,
            "error_rate": metrics.errors / total,
            "unique_users": len(metrics.user_ids),
            "avg_invocations_per_user": total / max(len(metrics.user_ids), 1),
            "avg_duration_ms": metrics.avg_duration_ms
        }
    
    def generate_report(self, skill_name: Optional[str] = None, days: int = 30) -> str:
        """Generate a comprehensive usage report"""
        lines = [
            "# Skill Usage Metrics Report",
            f"\n**Period:** Last {days} days",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            ""
        ]
        
        if skill_name:
            # Single skill report
            metrics = self.metrics.get(skill_name)
            if metrics:
                lines.extend(self._format_skill_report(skill_name, metrics, days))
            else:
                lines.append(f"No metrics found for skill '{skill_name}'")
        else:
            # Overview report
            summary = self.get_usage_summary(days)
            lines.extend([
                "## Overview",
                f"- Total Skills: {summary['total_skills']}",
                f"- Total Invocations: {summary['total_invocations']}",
                f"- Total Unique Users: {summary['total_unique_users']}",
                "",
                "## Top Skills by Usage",
                ""
            ])
            
            for i, skill in enumerate(summary['skill_summaries'][:10], 1):
                lines.append(f"{i}. **{skill['skill_name']}** - {skill['invocations']} invocations")
                lines.append(f"   - Success rate: {skill['success_rate']:.1%}")
                lines.append(f"   - Unique users: {skill['unique_users']}")
                lines.append("")
            
            # Trending section
            lines.extend([
                "## Trending (Last 7 Days)",
                ""
            ])
            
            trending = self.get_trending_skills(days=7, limit=5)
            for skill in trending:
                lines.append(f"- **{skill['skill_name']}**: {skill['recent_invocations']} recent uses")
        
        return '\n'.join(lines)
    
    def _format_skill_report(self, skill_name: str, metrics: SkillMetrics, days: int) -> List[str]:
        """Format report for a single skill"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Calculate period metrics
        period_invocations = sum(
            count for date, count in metrics.daily_usage.items()
            if datetime.fromisoformat(date) >= cutoff_date
        )
        
        return [
            f"## {skill_name}",
            "",
            "### Usage Summary",
            f"- Total Invocations: {metrics.total_invocations}",
            f"- Period Invocations: {period_invocations}",
            f"- Successful Completions: {metrics.successful_completions}",
            f"- Errors: {metrics.errors}",
            f"- Success Rate: {metrics.successful_completions / max(metrics.total_invocations, 1):.1%}",
            f"- Unique Users: {len(metrics.user_ids)}",
            f"- Average Duration: {metrics.avg_duration_ms:.0f}ms",
            "",
            "### Timeline",
            f"- First Used: {metrics.first_used[:10] if metrics.first_used else 'N/A'}",
            f"- Last Used: {metrics.last_used[:10] if metrics.last_used else 'N/A'}",
            ""
        ]


def main():
    """CLI for metrics tracker"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Skill Usage Metrics Tracker")
    parser.add_argument("--data-dir", default=".metrics", help="Metrics data directory")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Record command
    record_parser = subparsers.add_parser("record", help="Record a usage event")
    record_parser.add_argument("skill", help="Skill name")
    record_parser.add_argument("--type", default="invoke", choices=["invoke", "complete", "error"])
    record_parser.add_argument("--user", help="User ID")
    record_parser.add_argument("--duration", type=int, help="Duration in ms")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate usage report")
    report_parser.add_argument("--skill", help="Specific skill (default: overview)")
    report_parser.add_argument("--days", type=int, default=30, help="Days to include")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Get usage summary")
    summary_parser.add_argument("--days", type=int, default=30, help="Days to include")
    
    # Trending command
    trending_parser = subparsers.add_parser("trending", help="Get trending skills")
    trending_parser.add_argument("--days", type=int, default=7, help="Days to include")
    trending_parser.add_argument("--limit", type=int, default=10, help="Number of skills")
    
    # Funnel command
    funnel_parser = subparsers.add_parser("funnel", help="Get adoption funnel")
    funnel_parser.add_argument("skill", help="Skill name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    tracker = MetricsTracker(args.data_dir)
    
    if args.command == "record":
        tracker.record_event(
            args.skill,
            args.type,
            args.user,
            args.duration
        )
        print(f"✓ Recorded {args.type} event for '{args.skill}'")
    
    elif args.command == "report":
        report = tracker.generate_report(args.skill, args.days)
        print(report)
    
    elif args.command == "summary":
        summary = tracker.get_usage_summary(args.days)
        print(json.dumps(summary, indent=2))
    
    elif args.command == "trending":
        trending = tracker.get_trending_skills(args.days, args.limit)
        print(json.dumps(trending, indent=2))
    
    elif args.command == "funnel":
        funnel = tracker.get_adoption_funnel(args.skill)
        print(json.dumps(funnel, indent=2))


if __name__ == "__main__":
    main()

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

class Risk(BaseModel):
    title: str = Field(..., description="Risk title")
    description: str = Field(..., description="Risk description")
    impact: str = Field(..., description="Risk impact level (Low/Medium/High)")
    probability: str = Field(..., description="Risk probability (Low/Medium/High)")
    mitigation: str = Field(..., description="Suggested mitigation strategy")

class Task(BaseModel):
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    estimated_hours: int = Field(..., description="Estimated hours to complete")
    dependencies: List[str] = Field(default=[], description="List of dependent task names")
    can_parallel: bool = Field(default=False, description="Can this task be done in parallel with others")

class Milestone(BaseModel):
    name: str = Field(..., description="Milestone name")
    description: str = Field(..., description="Milestone description")
    week_number: int = Field(..., description="Target week number")
    deliverables: List[str] = Field(..., description="List of deliverables")
    tasks: List[Task] = Field(..., description="Tasks required for this milestone")
    success_criteria: List[str] = Field(..., description="Success criteria")

class Plan(BaseModel):
    project_name: str = Field(..., description="Project name")
    project_summary: str = Field(..., description="Brief project summary")
    total_weeks: int = Field(..., description="Total project duration in weeks")
    milestones: List[Milestone] = Field(..., description="Project milestones")
    risks: List[Risk] = Field(..., description="Top 3 project risks")
    monitoring_checkpoints: List[str] = Field(..., description="Key monitoring checkpoints")
    parallel_opportunities: List[str] = Field(..., description="Identified parallel work opportunities")

    def to_markdown(self) -> str:
        """Convert plan to human-readable markdown format"""
        md = f"# {self.project_name}\n\n"
        md += f"**Project Summary:** {self.project_summary}\n\n"
        md += f"**Total Duration:** {self.total_weeks} weeks\n\n"

        # Milestones
        md += "## Milestones\n\n"
        for milestone in self.milestones:
            md += f"### {milestone.name} (Week {milestone.week_number})\n"
            md += f"{milestone.description}\n\n"

            md += "**Deliverables:**\n"
            for deliverable in milestone.deliverables:
                md += f"- {deliverable}\n"

            md += "\n**Tasks:**\n"
            for task in milestone.tasks:
                parallel_note = " (Can be done in parallel)" if task.can_parallel else ""
                md += f"- **{task.name}** ({task.estimated_hours}h){parallel_note}\n"
                md += f"  {task.description}\n"
                if task.dependencies:
                    md += f"  Dependencies: {', '.join(task.dependencies)}\n"

            md += "\n**Success Criteria:**\n"
            for criteria in milestone.success_criteria:
                md += f"- {criteria}\n"
            md += "\n"

        # Risks
        md += "## Top 3 Risks\n\n"
        for i, risk in enumerate(self.risks, 1):
            md += f"### {i}. {risk.title}\n"
            md += f"**Description:** {risk.description}\n"
            md += f"**Impact:** {risk.impact} | **Probability:** {risk.probability}\n"
            md += f"**Mitigation:** {risk.mitigation}\n\n"

        # Monitoring
        md += "## Monitoring Checkpoints\n\n"
        for checkpoint in self.monitoring_checkpoints:
            md += f"- {checkpoint}\n"

        # Parallel Opportunities
        md += "\n## Parallel Work Opportunities\n\n"
        for opportunity in self.parallel_opportunities:
            md += f"- {opportunity}\n"

        return md

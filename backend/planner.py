import json
import os
from typing import Optional
from groq import Groq
from .models import Plan
from .utils import clean_json_response, validate_json_structure, format_error_message


class PlannerAgent:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"  # Updated to a supported model

    def generate_plan(self, project_brief: str) -> tuple[Optional[Plan], Optional[str]]:
        """
        Generate a project plan from a brief
        Returns: (Plan object, error message)
        """
        try:
            # Create prompt
            prompt = self._create_prompt(project_brief)
            # Call the LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert project manager who creates detailed, realistic "
                            "project plans. Always respond with valid JSON only."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            # Extract & parse JSON
            json_text = clean_json_response(response.choices[0].message.content)
            plan_data = json.loads(json_text)
            # Validate & build Plan
            plan_data = validate_json_structure(plan_data)
            plan = Plan(**plan_data)
            return plan, None

        except json.JSONDecodeError as e:
            return None, f"Invalid JSON response from AI: {e}"
        except Exception as e:
            return None, format_error_message(e)

    def _create_prompt(self, project_brief: str) -> str:
        """Build the exact JSON-only prompt for the model."""
        return f"""
Create a detailed project plan for the following project brief. Respond with ONLY valid JSON matching this exact structure:

{{
  "project_name": "string",
  "project_summary": "string",
  "total_weeks": number,
  "milestones": [
    {{
      "name": "string",
      "description": "string", 
      "week_number": number,
      "deliverables": ["string"],
      "tasks": [
        {{
          "name": "string",
          "description": "string",
          "estimated_hours": number,
          "dependencies": ["string"],
          "can_parallel": boolean
        }}
      ],
      "success_criteria": ["string"]
    }}
  ],
  "risks": [
    {{
      "title": "string",
      "description": "string",
      "impact": "Low|Medium|High",
      "probability": "Low|Medium|High",
      "mitigation": "string"
    }}
  ],
  "monitoring_checkpoints": ["string"],
  "parallel_opportunities": ["string"]
}}

Requirements:
- Realistic 4–12 week timeline
- Detailed tasks & hour estimates
- Exactly 3 risks with mitigations
- Mark parallel-capable tasks
- Include monitoring checkpoints

Project Brief:
{project_brief}

Respond with valid JSON only:
"""

def create_planner() -> tuple[Optional[PlannerAgent], Optional[str]]:
    """
    Factory: returns (PlannerAgent, None) if GROQ_API_KEY is set, else (None, error).
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None, "GROQ_API_KEY not found in environment variables"
    try:
        return PlannerAgent(api_key), None
    except Exception as e:
        return None, format_error_message(e)

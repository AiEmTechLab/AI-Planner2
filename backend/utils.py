import json
import re
from typing import Dict, Any

def clean_json_response(response: str) -> str:
    """Clean and extract JSON from LLM response"""
    # Remove markdown code blocks
    response = re.sub(r'```json\s*', '', response)
    response = re.sub(r'```\s*$', '', response)

    # Find JSON object in response
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        return json_match.group(0)

    return response.strip()

def validate_json_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and fix common JSON structure issues"""
    required_fields = {
        'project_name': 'Untitled Project',
        'project_summary': 'No summary provided',
        'total_weeks': 4,
        'milestones': [],
        'risks': [],
        'monitoring_checkpoints': [],
        'parallel_opportunities': []
    }

    # Ensure all required fields exist
    for field, default_value in required_fields.items():
        if field not in data:
            data[field] = default_value

    # Ensure risks list has exactly 3 items
    if len(data['risks']) < 3:
        while len(data['risks']) < 3:
            data['risks'].append({
                'title': 'Generic Risk',
                'description': 'Standard project risk',
                'impact': 'Medium',
                'probability': 'Medium',
                'mitigation': 'Monitor and adjust as needed'
            })
    elif len(data['risks']) > 3:
        data['risks'] = data['risks'][:3]

    return data

def format_error_message(error: Exception) -> str:
    """Format error message for user display"""
    error_type = type(error).__name__
    return f"Error ({error_type}): {str(error)}"

import time
import json
from typing import List


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.last_request_time = 0

    def wait_if_needed(self):
        """Wait if we're hitting rate limits."""
        current_time = time.time()
        min_interval = 60.0 / self.requests_per_minute

        if current_time - self.last_request_time < min_interval:
            wait_time = min_interval - (current_time - self.last_request_time)
            time.sleep(wait_time)

        self.last_request_time = time.time()


def compare_technologies(structured_outputs: dict, tech1: str, tech2: str):
    """Compare two technologies"""
    tech1_output = structured_outputs.get(tech1)
    tech2_output = structured_outputs.get(tech2)

    if not tech1_output or not tech2_output:
        return "One or both technologies not found."

    comparison_prompt = f"""
    Compare the following technologies based on their summary, main_techniques, applications

    {tech1_output.main_topic}:
    Summary: {tech1_output.summary}
    Main Techniques: {tech1_output.main_techniques}
    Applications: {tech1_output.applications}

    {tech2_output.main_topic}:
    Summary: {tech2_output.summary}
    Main Techniques: {tech2_output.main_techniques}
    Applications: {tech2_output.applications}
    """
    return comparison_prompt


def trace_evolution(structured_outputs: dict, technology: str):
    """Trace the evolution of a technology"""
    tech_output = structured_outputs.get(technology)
    if not tech_output:
        return "Technology not found."

    evolution_prompt = f"""
    Trace the evolution of the following technology:

    {tech_output.main_topic}:
    Summary: {tech_output.summary}
    Evolution Timeline: {tech_output.evolution_timeline}
    Major Contributors: {tech_output.major_contributors}
    Key Innovations: {tech_output.key_innovations}
    """
    return evolution_prompt


def create_function_schemas(valid_technologies: List[str]):
    """Create OpenAI function schemas for comparison and evolution tracing"""
    compare_schema = {
        "type": "function",
        "function": {
            "name": "compare_technologies",
            "description": "Compare two technologies",
            "parameters": {
                "type": "object",
                "properties": {
                    "tech1": {
                        "type": "string",
                        "description": "The first technology to compare",
                        "enum": valid_technologies
                    },
                    "tech2": {
                        "type": "string",
                        "description": "The second technology to compare",
                        "enum": valid_technologies
                    }
                },
                "required": ["tech1", "tech2"]
            }
        }
    }

    trace_schema = {
        "type": "function",
        "function": {
            "name": "trace_evolution",
            "description": "Trace the historical evolution of a given technology",
            "parameters": {
                "type": "object",
                "properties": {
                    "technology": {
                        "type": "string",
                        "description": "The technology to trace",
                        "enum": valid_technologies
                    }
                },
                "required": ["technology"]
            }
        }
    }

    return compare_schema, trace_schema
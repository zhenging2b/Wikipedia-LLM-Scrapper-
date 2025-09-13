from pydantic import BaseModel, Field
from typing import List, Optional
import json

class WikipediaExtraction(BaseModel):
  """Schema for artificial intelligence subfield"""
  main_topic: str = Field(description="The name of the AI subfield (e.g., Machine Learning, Expert Systems, Computer Vision)")
  summary: str = Field(desciption="Concise overview of the subfield, its purpose, and scope")
  evolution_timeline: str = Field(description="Chronological evolution of this subfield, with notable milestones across time")
  key_innovations: str = Field(description="The most important breakthroughs, inventions, or discoveries that shaped this subfield")
  major_contributors: str = Field(description="Key researchers, organizations, or companies that significantly advanced this subfield")
  main_techniques: List[str] = Field(description="Core methods, models, or algorithms commonly used in this subfield")
  applications: List[str] = Field(description="Practical use cases and domains where this subfield has had major impact")

# Let's see what the JSON schema looks like
print("📋 Generated JSON Schema Preview:")
print(json.dumps(WikipediaExtraction.model_json_schema(), indent=2))
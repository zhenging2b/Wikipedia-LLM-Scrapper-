import json
from typing import List, Dict, Optional, Any
from openai import OpenAI
from .models import WikipediaExtraction
from .utils import RateLimiter, compare_technologies, trace_evolution, create_function_schemas

class OptimizedProcessor:
    """
    Optimized processor for high-throughput applications.

    Features:
    - Batch processing for efficiency
    - Async operations for concurrent requests
    - Caching to reduce API calls
    - Rate limiting to respect API limits
    """

    def __init__(self,client:Optional[OpenAI] = None):
      self.client = client
      self.cache = {}
      self.rate_limiter = RateLimiter(requests_per_minute=60)



    def extract_strucutred_data(self, content: str, model: str = "gpt-4o-mini") -> WikipediaExtraction:
    #create schema for Open AI
      schema = {
          "name": "AI_subfield_catalog",
          "schema": {
              **WikipediaExtraction.model_json_schema(),
              "additionalProperties": False
          },
          "strict": True  # This enforces strict schema compliance
      }
      try:
        # The magic happens here - response_format enforces our schema
        response = self.client.chat.completions.create(
            model=model,  # Only gpt-4o and gpt-4o-mini support structured outputs
            messages=[
                {
                    "role": "system",
                    "content": "Extract AI subfield information from text and structure it exactly according to the provided schema."
                },
                {
                    "role": "user",
                    "content": f"Extract and analyze AI subfield data from:\n\n{content}"
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": schema
            }
        )
        # Direct validation - no parsing errors possible!
        ai_subfield = WikipediaExtraction.model_validate_json(response.choices[0].message.content)

        print("✅ Structured extraction successful!")
        return ai_subfield
      except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return None

    def batch_extract(self, articles: List[Dict]) -> List[WikipediaExtraction]:
      final_dic= {}
      for dic in articles:
        current_title = dic["title"]
        # Check cache first
        cache_key = hash(dic["raw_content"][:100])
        if cache_key in self.cache:
          print("💾 Using cached result")
          final_dic[self.cache[cache_key].main_topic] = (self.cache[cache_key])
          continue
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        #Process content
        result = self.extract_strucutred_data(dic["raw_content"])
        if result:
          self.cache[cache_key] = result
          final_dic[result.main_topic] = result
        else:
          print(f"Extraction failed for {current_title}")
      return final_dic

    def demonstrate_function_calling(self, structured_outputs: Dict[str, WikipediaExtraction],
                                     natural_queries: List[str]) -> List[str]:
        """Demonstrate function calling with natural language queries"""
        if not self.client:
            print("❌ OpenAI client not initialized. Exiting.")
            return []

        valid_technologies = list(structured_outputs.keys())
        compare_schema, trace_schema = create_function_schemas(valid_technologies)

        results = []
        for query in natural_queries:
            print(f"🔍 Query: {query}")
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""You are a helpful research assistant with access to detailed data for these technologies: {valid_technologies}.
                            Use the relevant function to answer questions about comparisons or evolution."""
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    tools=[compare_schema, trace_schema],
                    tool_choice="auto"
                )

                response_message = response.choices[0].message

                if response_message.tool_calls:
                    tool_call = response_message.tool_calls[0]
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    print(f"🔧 LLM decided to call: {function_name}({function_args})")

                    # Execute the function
                    if function_name == "compare_technologies":
                        result = compare_technologies(structured_outputs, **function_args)
                    elif function_name == "trace_evolution":
                        result = trace_evolution(structured_outputs, **function_args)

                    if result:
                        final_response = self.client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {
                                    "role": "system",
                                    "content": f"Use this context to answer the user query: {result}"
                                },
                                {
                                    "role": "user",
                                    "content": query
                                }
                            ]
                        )
                        answer = final_response.choices[0].message.content
                        print(answer)
                        results.append(answer)
                    else:
                        results.append("Could not generate comparison/evolution data")
                else:
                    results.append("No function supports this query")

            except Exception as e:
                print(f"⚠️ Error processing query: {e}")
                results.append(f"Error: {e}")

        return results
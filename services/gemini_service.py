"""
Gemini Service - Handles all interactions with Google's Gemini AI API
"""

import json
import logging
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiService:
    """Service class for interacting with Gemini AI to generate test cases."""

    def __init__(self, model_name="gemini-2.5-pro", temperature=0):
        """
        Initialize the Gemini service.

        Args:
            model_name (str): The Gemini model to use
            temperature (float): Temperature for response generation (0 = deterministic)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the Gemini LLM instance."""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                convert_system_message_to_human=True
            )
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini LLM: {str(e)}")

    def _create_prompt(self, user_story):
        """
        Create the prompt for test case generation.

        Args:
            user_story (str): The user story text

        Returns:
            str: Formatted prompt for the LLM
        """
        return f"""You are a professional SDET. Generate test cases for the following user story.

User Story:
{user_story}

Generate a comprehensive set of test cases covering all acceptance criteria.

IMPORTANT: Return ONLY a valid JSON array with no additional text, explanations, or markdown formatting.

Each test case must have these EXACT field names:
- "Test Case ID" (format: TC001, TC002, etc.)
- "Test Case Title" (brief description)
- "Steps" (numbered steps separated by \\n)
- "Expected Result" (what should happen)
- "Linked Acceptance Criterion" (e.g., AC1, AC2, etc.)

Example format:
[
  {{
    "Test Case ID": "TC001",
    "Test Case Title": "Successful login with valid credentials",
    "Steps": "1. Navigate to login page\\n2. Enter valid email\\n3. Enter valid password\\n4. Click Login button",
    "Expected Result": "User is successfully logged in and redirected to dashboard",
    "Linked Acceptance Criterion": "AC1"
  }}
]

Generate the JSON array now:"""

    def _clean_response(self, content):
        """
        Clean the LLM response by removing markdown code blocks.

        Args:
            content (str): Raw response from LLM

        Returns:
            str: Cleaned JSON string
        """
        content = content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```"):
            lines = content.split("\n")
            json_lines = []
            in_code_block = False

            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or (not line.strip().startswith("```")):
                    json_lines.append(line)

            content = "\n".join(json_lines).strip()

        return content

    def generate_test_cases(self, user_story):
        """
        Generate test cases from a user story.

        Args:
            user_story (str): The user story text with description and acceptance criteria

        Returns:
            dict: Result dictionary with success status and test cases or error message
                {
                    "success": bool,
                    "test_cases": list (if success),
                    "count": int (if success),
                    "error": str (if failure)
                }
        """
        try:
            # Validate input
            if not user_story or not user_story.strip():
                return {
                    "success": False,
                    "error": "User story cannot be empty"
                }

            # Create prompt
            prompt = self._create_prompt(user_story)

            # Get response from LLM
            response = self.llm.invoke(prompt)
            content = response.content

            # Clean the response
            cleaned_content = self._clean_response(content)

            # Parse JSON
            test_cases = json.loads(cleaned_content)

            # Ensure it's a list
            if not isinstance(test_cases, list):
                test_cases = [test_cases]

            # Validate test cases
            if not test_cases or len(test_cases) == 0:
                return {
                    "success": False,
                    "error": "No test cases were generated"
                }

            # Validate structure of each test case
            required_fields = ['Test Case ID', 'Test Case Title', 'Steps',
                               'Expected Result', 'Linked Acceptance Criterion']

            for i, tc in enumerate(test_cases):
                if not isinstance(tc, dict):
                    return {
                        "success": False,
                        "error": f"Test case {i+1} is not a valid object"
                    }

                missing_fields = [field for field in required_fields if field not in tc]
                if missing_fields:
                    return {
                        "success": False,
                        "error": f"Test case {i+1} is missing fields: {', '.join(missing_fields)}"
                    }

            return {
                "success": True,
                "test_cases": test_cases,
                "count": len(test_cases)
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse JSON response: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    def get_model_info(self):
        """
        Get information about the current model configuration.

        Returns:
            dict: Model information
        """
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "status": "initialized" if self.llm else "not initialized"
        }
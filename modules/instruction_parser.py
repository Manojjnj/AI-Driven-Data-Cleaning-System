import os
import json
from openai import OpenAI


class InstructionParser:

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def extract_commands(self, instruction_text, columns):

        prompt = f"""
You are a data transformation engine.

Dataset columns:
{columns}

Convert the following instruction into structured JSON.

Supported actions:
- remove_rows
- drop_column
- fill_missing
- remove_duplicates
- rename_column

Instruction:
{instruction_text}

Return ONLY valid JSON.
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.choices[0].message.content)

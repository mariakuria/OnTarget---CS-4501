"""Test doubles. No test ever calls a real LLM."""
import json


class FakeLLM:
    """Stands in for the LLM. Records prompts, returns a canned answer or raises."""

    def __init__(self, response="", error=None):
        self.response = response
        self.error = error
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return self.response


class FlakyLLM:
    """Returns or raises the given outcomes in order, then repeats the last one."""

    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        outcome = self.outcomes[min(len(self.prompts) - 1, len(self.outcomes) - 1)]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def llm_plan_json(n, company="Amazon", problem_id="two-sum"):
    """A valid LLM answer with n days."""
    days = []
    for i in range(n):
        days.append(
            {
                "title": f"{company} focus day {i + 1}",
                "tasks": [
                    {"type": "coding", "text": "Solve Two Sum", "problem_id": problem_id},
                    {"type": "behavioral", "text": f"Write a story for {company}"},
                ],
            }
        )
    return json.dumps({"days": days})

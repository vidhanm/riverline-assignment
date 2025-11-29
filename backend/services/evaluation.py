import re
import json
from services.llm import get_llm_response


def evaluate_conversation(transcript, goal):
    """
    Evaluate conversation using LLM-as-judge pattern
    Returns: {"task_completion": int, "naturalness": int, "goal_achieved": int, "feedback": str}
    """
    # Format transcript for readability
    formatted_transcript = "\n".join([
        f"{turn['persona']} ({turn['agent']}): {turn['text']}"
        for turn in transcript
    ])

    # Check if conversation is in Hindi (simple heuristic)
    is_hindi = any("हिंदी" in turn['text'] or any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in turn['text']) for turn in transcript if 'text' in turn)

    language_note = ""
    if is_hindi:
        language_note = "\n\nNOTE: This conversation is conducted in Hindi (Devanagari script). Evaluate naturalness based on Hindi language norms and cultural appropriateness for Indian debt collection context."

    prompt = f"""Evaluate this conversation:

{formatted_transcript}

Scenario Goal: {goal}{language_note}

Score 1-10 for:
- task_completion: Did they complete the conversation goal?
- naturalness: Does it sound like a natural conversation?
- goal_achieved: How well was the goal met?

Return ONLY valid JSON in this exact format:
{{"task_completion": X, "naturalness": X, "goal_achieved": X, "feedback": "brief explanation"}}"""

    try:
        response = get_llm_response(prompt, max_tokens=300)

        # Extract JSON from response (handles markdown code blocks)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            scores = json.loads(json_match.group())

            # Validate required fields
            required = ["task_completion", "naturalness", "goal_achieved", "feedback"]
            if all(k in scores for k in required):
                return scores

        # Fallback if parsing fails
        return {
            "task_completion": 5,
            "naturalness": 5,
            "goal_achieved": 5,
            "feedback": "Evaluation parse error"
        }

    except Exception as e:
        print(f"Evaluation failed: {e}")
        return {
            "task_completion": 5,
            "naturalness": 5,
            "goal_achieved": 5,
            "feedback": f"Error: {str(e)}"
        }

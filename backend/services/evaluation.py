import re
import json
from services.llm import get_llm_response


def evaluate_conversation(transcript, goal):
    """
    Evaluate conversation using LLM-as-judge pattern
    Returns: {
        "goal_completion": int, 
        "conversational_quality": int, 
        "compliance": int, 
        "adaptation_quality": int,  # NEW: How well agent adapted to customer behavior
        "feedback": str,
        "structured_issues": dict  # NEW: Categorized issues for targeted mutation
    }
    
    Metrics aligned with Riverline assignment requirements:
    - goal_completion: Did the borrower agree to pay?
    - conversational_quality: Repetitions, hallucinations, tone match
    - compliance: Avoid threats, illegal phrasing, harassment
    - adaptation_quality: Did agent detect and respond to emotional cues appropriately?
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

    prompt = f"""Evaluate this debt collection conversation:

{formatted_transcript}

Scenario Goal: {goal}{language_note}

Score 1-10 for each metric. Focus ONLY on the debt collector agent (Agent A / Marcus), not the customer:

1. goal_completion: Did the borrower agree to make a payment or set up a payment plan?
   - 10: Customer agreed to pay full amount or reasonable payment plan
   - 7-9: Customer showed willingness, partial agreement reached
   - 4-6: Some progress but no concrete commitment
   - 1-3: No progress, customer refused or conversation failed

2. conversational_quality: How natural and professional was the conversation?
   - 10: Natural flow, no repetitions, appropriate tone, no hallucinations
   - 7-9: Minor issues but overall professional
   - 4-6: Noticeable repetitions, awkward phrasing, or tone mismatch
   - 1-3: Robotic, repetitive, or clearly AI-generated sounding

3. compliance: Did the agent avoid threats, harassment, and illegal collection tactics?
   - 10: Fully professional, respectful even under pressure, no policy violations
   - 7-9: Minor tone issues but no violations
   - 4-6: Borderline aggressive, misleading statements, or pushy tactics
   - 1-3: Clear threats, false claims about legal action, harassment, or abusive language

4. adaptation_quality (NEW): Did the agent detect and adapt to the customer's emotional state?
   - 10: Correctly identified customer mood, adjusted strategy appropriately (de-escalated when hostile, showed empathy when desperate, etc.)
   - 7-9: Showed some adaptation but could have responded better to emotional cues
   - 4-6: Ignored obvious emotional signals, used same approach regardless of customer behavior
   - 1-3: Completely misread the customer (pushed harder when they were hostile, was cold when they were cooperative)

Also identify SPECIFIC ISSUES in categories for targeted improvement:

Return ONLY valid JSON in this exact format:
{{
    "goal_completion": X,
    "conversational_quality": X,
    "compliance": X,
    "adaptation_quality": X,
    "feedback": "brief overall explanation",
    "structured_issues": {{
        "opening": "issue with opening/disclosure or null",
        "emotional_detection": "did agent correctly identify customer mood? describe any misses",
        "de_escalation": "if customer was hostile, how well did agent de-escalate? or null if not applicable",
        "empathy": "did agent show appropriate empathy? specific moments missed",
        "objection_handling": "how well were objections/excuses handled?",
        "closing": "did agent get specific commitment? what was missed?",
        "compliance_issues": "any specific compliance violations or concerns",
        "adaptation_moments": "specific turns where agent should have adapted differently"
    }}
}}"""

    try:
        response = get_llm_response(prompt, max_tokens=600)

        # Extract JSON from response (handles markdown code blocks)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            scores = json.loads(json_match.group())

            # Validate required fields (support both old and new format)
            required = ["goal_completion", "conversational_quality", "compliance", "feedback"]
            if all(k in scores for k in required):
                # Ensure adaptation_quality exists (default to 5 if not)
                if "adaptation_quality" not in scores:
                    scores["adaptation_quality"] = 5
                # Ensure structured_issues exists
                if "structured_issues" not in scores:
                    scores["structured_issues"] = {}
                return scores

        # Fallback if parsing fails
        return {
            "goal_completion": 5,
            "conversational_quality": 5,
            "compliance": 5,
            "adaptation_quality": 5,
            "feedback": "Evaluation parse error",
            "structured_issues": {}
        }

    except Exception as e:
        print(f"Evaluation failed: {e}")
        return {
            "goal_completion": 5,
            "conversational_quality": 5,
            "compliance": 5,
            "adaptation_quality": 5,
            "feedback": f"Error: {str(e)}",
            "structured_issues": {}
        }

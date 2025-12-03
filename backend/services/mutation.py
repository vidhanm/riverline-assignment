import json
from services.llm import get_llm_response
from services.vector_store import search_similar


def extract_patterns(evaluations, success_examples, failure_examples):
    """
    NEW: Extract specific patterns that differentiate success from failure.
    This provides focused guidance for mutations instead of just showing examples.
    """
    # Aggregate structured issues from evaluations
    all_issues = {
        "opening": [],
        "emotional_detection": [],
        "de_escalation": [],
        "empathy": [],
        "objection_handling": [],
        "closing": [],
        "compliance_issues": [],
        "adaptation_moments": []
    }
    
    for eval_data in evaluations:
        structured = eval_data.get('structured_issues', {})
        for key in all_issues:
            if structured.get(key) and structured[key] != "null":
                all_issues[key].append(structured[key])
    
    # Build pattern extraction prompt
    pattern_prompt = f"""Analyze these debt collection conversations to extract SPECIFIC PATTERNS.

=== SUCCESSFUL CONVERSATION EXCERPTS (score >= 8) ===
{success_examples}

=== FAILED CONVERSATION EXCERPTS (score < 5) ===
{failure_examples}

=== SPECIFIC ISSUES IDENTIFIED ===
Opening problems: {'; '.join(all_issues['opening'][:3]) or 'None noted'}
Emotional detection issues: {'; '.join(all_issues['emotional_detection'][:3]) or 'None noted'}
De-escalation problems: {'; '.join(all_issues['de_escalation'][:3]) or 'None noted'}
Empathy gaps: {'; '.join(all_issues['empathy'][:3]) or 'None noted'}
Objection handling: {'; '.join(all_issues['objection_handling'][:3]) or 'None noted'}
Closing issues: {'; '.join(all_issues['closing'][:3]) or 'None noted'}
Compliance concerns: {'; '.join(all_issues['compliance_issues'][:3]) or 'None noted'}
Adaptation failures: {'; '.join(all_issues['adaptation_moments'][:3]) or 'None noted'}

=== YOUR TASK ===
Extract the TOP 5 specific behavioral patterns that differentiate success from failure:

For each pattern, identify:
1. What successful agents DO that failed agents DON'T
2. What triggers this behavior (customer signal to watch for)
3. Exact phrasing or approach that works

Return a JSON object:
{{
    "success_patterns": [
        {{
            "pattern": "description of what works",
            "trigger": "customer signal that should activate this",
            "example_phrase": "actual words/approach to use"
        }}
    ],
    "failure_patterns": [
        {{
            "pattern": "what to avoid",
            "why_fails": "why this approach backfires"
        }}
    ],
    "key_insight": "single most important insight for improvement"
}}"""

    try:
        response = get_llm_response(pattern_prompt, max_tokens=600)
        # Extract JSON
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"Pattern extraction failed: {e}")
    
    return {
        "success_patterns": [],
        "failure_patterns": [],
        "key_insight": "Unable to extract patterns"
    }


def generate_mutation(current_prompt, persona_name, evaluations, scenario_names):
    """
    Generate improved system prompt based on evaluation history across MULTIPLE scenarios.
    
    ENHANCED: Now includes pattern extraction step for more targeted mutations.

    Args:
        current_prompt: Current persona system prompt
        persona_name: Name of persona (for vector search)
        evaluations: List of recent evaluations with scores/feedback
        scenario_names: List of scenario names tested (e.g., ["Angry Customer", "Evasive Customer"])

    Returns:
        dict with:
            - mutated_prompt: New system prompt
            - metadata: Reasoning data (success/failure examples, feedback, scores, patterns)
            - reasoning_prompt: Full prompt sent to LLM
    """
    # Calculate average scores (now including adaptation_quality)
    avg_scores = {
        'goal_completion': sum(e.get('goal_completion', e.get('task_completion', 5)) for e in evaluations) / len(evaluations),
        'conversational_quality': sum(e.get('conversational_quality', e.get('naturalness', 5)) for e in evaluations) / len(evaluations),
        'compliance': sum(e.get('compliance', 5) for e in evaluations) / len(evaluations),
        'adaptation_quality': sum(e.get('adaptation_quality', 5) for e in evaluations) / len(evaluations)
    }
    overall_avg = sum(avg_scores.values()) / len(avg_scores)

    # Find successful examples from vector store (score >= 8)
    # Search broadly across ALL scenarios to find generalizable patterns
    try:
        success_results = search_similar(
            f"{persona_name} successful conversation across contexts",
            k=5,  # Get more examples for better generalization
            filter_dict={"overall_score": {"$gte": 8.0}, "persona_a": persona_name}
            # Note: Not filtering by scenario - want patterns that work across contexts
        )
        success_examples = "\n\n".join([
            f"SUCCESS EXAMPLE (score {success_results['metadatas'][0][i]['overall_score']}):\n{success_results['documents'][0][i][:500]}..."
            for i in range(len(success_results['ids'][0]))
        ]) if success_results['ids'][0] else "No high-scoring examples found"
    except Exception as e:
        print(f"Error fetching success examples: {e}")
        success_examples = "No high-scoring examples found"

    # Find failure examples (score < 5)
    try:
        failure_results = search_similar(
            f"{persona_name} failed conversation",
            k=3,  # Get more failure patterns to avoid
            filter_dict={"overall_score": {"$lt": 5.0}, "persona_a": persona_name}
        )
        failure_examples = "\n\n".join([
            f"FAILURE EXAMPLE (score {failure_results['metadatas'][0][i]['overall_score']}):\n{failure_results['documents'][0][i][:500]}..."
            for i in range(len(failure_results['ids'][0]))
        ]) if failure_results['ids'][0] else "No low-scoring examples found"
    except Exception as e:
        print(f"Error fetching failure examples: {e}")
        failure_examples = "No low-scoring examples found"

    # Aggregate feedback
    all_feedback = [e.get('feedback', '') for e in evaluations if e.get('feedback')]
    
    # NEW: Extract patterns from examples (chain-of-thought for evolution)
    patterns = extract_patterns(evaluations, success_examples, failure_examples)
    
    # Format patterns for mutation prompt
    success_pattern_text = ""
    if patterns.get('success_patterns'):
        success_pattern_text = "\n".join([
            f"  - {p['pattern']} (Trigger: {p.get('trigger', 'N/A')}) Example: \"{p.get('example_phrase', 'N/A')}\""
            for p in patterns['success_patterns'][:5]
        ])
    
    failure_pattern_text = ""
    if patterns.get('failure_patterns'):
        failure_pattern_text = "\n".join([
            f"  - AVOID: {p['pattern']} (Why: {p.get('why_fails', 'N/A')})"
            for p in patterns['failure_patterns'][:3]
        ])

    # Build mutation prompt with pattern-informed guidance
    mutation_prompt = f"""You are evolving an AI agent's system prompt to improve performance across MULTIPLE scenarios.

CURRENT PROMPT:
{current_prompt}

TESTED ACROSS {len(scenario_names)} SCENARIOS:
{chr(10).join(f"- {name}" for name in scenario_names)}

PERFORMANCE DATA (last {len(evaluations)} simulations across these scenarios):
- Average goal completion: {avg_scores['goal_completion']:.1f}/10
- Average conversational quality: {avg_scores['conversational_quality']:.1f}/10
- Average compliance: {avg_scores['compliance']:.1f}/10
- Average adaptation quality: {avg_scores['adaptation_quality']:.1f}/10
- Overall average: {overall_avg:.1f}/10

=== KEY INSIGHT FROM PATTERN ANALYSIS ===
{patterns.get('key_insight', 'No clear insight extracted')}

=== SUCCESS PATTERNS TO EMBED IN PROMPT ===
{success_pattern_text or 'No clear success patterns found'}

=== FAILURE PATTERNS TO EXPLICITLY AVOID ===
{failure_pattern_text or 'No clear failure patterns found'}

FEEDBACK FROM EVALUATIONS:
{chr(10).join(f"- {fb}" for fb in all_feedback)}

TASK:
Generate an improved system prompt that:
1. Keeps the core personality of {persona_name}
2. **EMBEDS the success patterns as explicit instructions**
3. **INCLUDES warnings about failure patterns to avoid**
4. Addresses the weaknesses shown in feedback
5. **ADDS behavioral detection**: Agent should identify customer emotional state and adapt
6. Maintains appropriate tone and role
7. **CRITICAL: Must work well across ALL {len(scenario_names)} different scenarios/contexts**
8. **Include ADAPTIVE STRATEGIES**: Different approaches for hostile, evasive, desperate, cooperative customers
9. **Be ROBUST and GENERALIZABLE, not optimized for just one situation**

Return ONLY the new system prompt, nothing else. No explanations or meta-commentary."""

    # Generate mutation
    mutated_prompt = get_llm_response(mutation_prompt, max_tokens=800)  # Increased for richer prompts

    # Package metadata for visualization
    metadata = {
        'avg_scores': avg_scores,
        'overall_avg': overall_avg,
        'feedback_used': all_feedback,
        'success_examples': success_examples[:500] if success_examples else None,  # Truncate for storage
        'failure_examples': failure_examples[:500] if failure_examples else None,
        'patterns_extracted': patterns,  # NEW: Include extracted patterns
        'scenarios_tested': scenario_names,
        'num_evaluations': len(evaluations)
    }

    return {
        'mutated_prompt': mutated_prompt.strip(),
        'metadata': metadata,
        'reasoning_prompt': mutation_prompt
    }

import json
from services.llm import get_llm_response
from services.vector_store import search_similar


def generate_mutation(current_prompt, persona_name, evaluations, scenario_names):
    """
    Generate improved system prompt based on evaluation history across MULTIPLE scenarios

    Args:
        current_prompt: Current persona system prompt
        persona_name: Name of persona (for vector search)
        evaluations: List of recent evaluations with scores/feedback
        scenario_names: List of scenario names tested (e.g., ["Angry Customer", "Evasive Customer"])

    Returns:
        dict with:
            - mutated_prompt: New system prompt
            - metadata: Reasoning data (success/failure examples, feedback, scores)
            - reasoning_prompt: Full prompt sent to LLM
    """
    # Calculate average scores (using new metric names aligned with assignment)
    avg_scores = {
        'goal_completion': sum(e.get('goal_completion', e.get('task_completion', 5)) for e in evaluations) / len(evaluations),
        'conversational_quality': sum(e.get('conversational_quality', e.get('naturalness', 5)) for e in evaluations) / len(evaluations),
        'compliance': sum(e.get('compliance', 5) for e in evaluations) / len(evaluations)
    }
    overall_avg = sum(avg_scores.values()) / 3

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

    # Build mutation prompt
    mutation_prompt = f"""You are evolving an AI agent's system prompt to improve performance across MULTIPLE scenarios.

CURRENT PROMPT:
{current_prompt}

TESTED ACROSS {len(scenario_names)} SCENARIOS:
{chr(10).join(f"- {name}" for name in scenario_names)}

PERFORMANCE DATA (last {len(evaluations)} simulations across these scenarios):
- Average goal completion: {avg_scores['goal_completion']:.1f}/10
- Average conversational quality: {avg_scores['conversational_quality']:.1f}/10
- Average compliance: {avg_scores['compliance']:.1f}/10
- Overall average: {overall_avg:.1f}/10

FEEDBACK FROM EVALUATIONS:
{chr(10).join(f"- {fb}" for fb in all_feedback)}

HIGH-PERFORMING EXAMPLES TO LEARN FROM:
{success_examples}

LOW-PERFORMING EXAMPLES TO AVOID:
{failure_examples}

TASK:
Generate an improved system prompt that:
1. Keeps the core personality of {persona_name}
2. Addresses the weaknesses shown in feedback
3. Adopts successful patterns from high-scoring examples
4. Avoids failed patterns from low-scoring examples
5. Maintains appropriate tone and role
6. **CRITICAL: Must work well across ALL {len(scenario_names)} different scenarios/contexts**
7. **Be ROBUST and GENERALIZABLE, not optimized for just one situation**

Return ONLY the new system prompt, nothing else. No explanations or meta-commentary."""

    # Generate mutation
    mutated_prompt = get_llm_response(mutation_prompt, max_tokens=500)

    # Package metadata for visualization
    metadata = {
        'avg_scores': avg_scores,
        'overall_avg': overall_avg,
        'feedback_used': all_feedback,
        'success_examples': success_examples[:500] if success_examples else None,  # Truncate for storage
        'failure_examples': failure_examples[:500] if failure_examples else None,
        'scenarios_tested': scenario_names,
        'num_evaluations': len(evaluations)
    }

    return {
        'mutated_prompt': mutated_prompt.strip(),
        'metadata': metadata,
        'reasoning_prompt': mutation_prompt
    }

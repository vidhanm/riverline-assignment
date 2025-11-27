import json
from services.llm import get_llm_response
from services.vector_store import search_similar


def generate_mutation(current_prompt, persona_name, evaluations, scenario_name):
    """
    Generate improved system prompt based on evaluation history

    Args:
        current_prompt: Current persona system prompt
        persona_name: Name of persona (for vector search)
        evaluations: List of recent evaluations with scores/feedback
        scenario_name: Scenario type for context

    Returns:
        New mutated system prompt
    """
    # Calculate average scores
    avg_scores = {
        'task_completion': sum(e['task_completion'] for e in evaluations) / len(evaluations),
        'naturalness': sum(e['naturalness'] for e in evaluations) / len(evaluations),
        'goal_achieved': sum(e['goal_achieved'] for e in evaluations) / len(evaluations)
    }
    overall_avg = sum(avg_scores.values()) / 3

    # Find successful examples from vector store (score >= 8)
    try:
        success_results = search_similar(
            f"{persona_name} {scenario_name} successful conversation",
            k=3,
            filter_dict={"overall_score": {"$gte": 8.0}, "persona_a": persona_name}
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
            f"{persona_name} {scenario_name} failed conversation",
            k=2,
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
    mutation_prompt = f"""You are evolving an AI agent's system prompt to improve performance.

CURRENT PROMPT:
{current_prompt}

PERFORMANCE DATA (last {len(evaluations)} simulations):
- Average task completion: {avg_scores['task_completion']:.1f}/10
- Average naturalness: {avg_scores['naturalness']:.1f}/10
- Average goal achieved: {avg_scores['goal_achieved']:.1f}/10
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

Return ONLY the new system prompt, nothing else. No explanations or meta-commentary."""

    # Generate mutation
    mutated_prompt = get_llm_response(mutation_prompt, max_tokens=500)

    return mutated_prompt.strip()

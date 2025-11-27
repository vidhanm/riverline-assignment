from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from services.mutation import generate_mutation
from routers.simulations import run_simulation

router = APIRouter(prefix="/api/evolve", tags=["evolution"])


# Evolution configuration
N_BASELINE_SIMS = 5  # Test simulations for baseline
FAILURE_THRESHOLD = 8.5  # Trigger evolution if below this
N_MUTATIONS = 3  # Number of mutation variants
N_MUTATION_TESTS = 5  # Test simulations per mutation (same as baseline for fair comparison)


@router.post("/{persona_id}")
def evolve_persona(persona_id: int, scenario_ids: str, db: Session = Depends(get_db)):
    """
    Run evolution cycle for a persona against MULTIPLE scenarios

    Process:
    1. Run N baseline simulations (distributed across scenarios)
    2. Check if evolution needed (avg score < threshold)
    3. Generate N mutations
    4. Test each mutation (distributed across scenarios)
    5. Pick best mutation
    6. Save as new version

    Args:
        persona_id: ID of persona to evolve
        scenario_ids: Comma-separated scenario IDs (e.g., "1,2,3,4,5")
    """
    # Get persona
    persona = db.query(models.Persona).filter(models.Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Parse and validate scenarios
    try:
        scenario_id_list = [int(s.strip()) for s in scenario_ids.split(',')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scenario_ids format. Use comma-separated integers.")

    scenarios = db.query(models.Scenario).filter(
        models.Scenario.id.in_(scenario_id_list)
    ).all()

    if len(scenarios) != len(scenario_id_list):
        raise HTTPException(status_code=404, detail="Some scenarios not found")

    print(f"\n{'='*60}")
    print(f"EVOLUTION CYCLE: {persona.name}")
    print(f"Testing across {len(scenarios)} scenarios:")
    for s in scenarios:
        print(f"  - {s.name}")
    print(f"{'='*60}\n")

    # Step 1: Run baseline simulations (distributed across scenarios)
    print(f"Step 1: Running {N_BASELINE_SIMS} baseline simulations...")
    baseline_scores = []
    baseline_evaluations = []

    for i in range(N_BASELINE_SIMS):
        scenario = scenarios[i % len(scenarios)]  # Round-robin distribution
        print(f"  Baseline {i+1}/{N_BASELINE_SIMS} (vs {scenario.name})...")
        sim_run = run_simulation(scenario.id, db)

        # Get evaluation
        evaluation = db.query(models.Evaluation).filter(
            models.Evaluation.run_id == sim_run.id
        ).first()

        if evaluation:
            baseline_scores.append(evaluation.overall_score)
            baseline_evaluations.append({
                'task_completion': evaluation.scores['task_completion'],
                'naturalness': evaluation.scores['naturalness'],
                'goal_achieved': evaluation.scores['goal_achieved'],
                'feedback': evaluation.feedback
            })

    avg_baseline = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0
    print(f"\n  Baseline average: {avg_baseline:.2f}/10")

    # Step 2: Check if evolution needed
    if avg_baseline >= FAILURE_THRESHOLD:
        print(f"  Score above threshold ({FAILURE_THRESHOLD}). No evolution needed.")
        return {
            "evolved": False,
            "reason": "Score above threshold",
            "baseline_score": avg_baseline,
            "threshold": FAILURE_THRESHOLD
        }

    print(f"  Score below threshold! Triggering evolution...")

    # Step 3: Generate mutations
    print(f"\nStep 2: Generating {N_MUTATIONS} mutations...")
    mutations = []

    for i in range(N_MUTATIONS):
        print(f"  Generating mutation {i+1}/{N_MUTATIONS}...")
        mutated_prompt = generate_mutation(
            current_prompt=persona.system_prompt,
            persona_name=persona.name,
            evaluations=baseline_evaluations,
            scenario_names=[s.name for s in scenarios]  # Pass ALL scenario names
        )
        mutations.append(mutated_prompt)

    # Step 4: Test each mutation
    print(f"\nStep 3: Testing mutations...")
    mutation_results = []

    for mut_idx, mutated_prompt in enumerate(mutations):
        print(f"\n  Testing mutation {mut_idx+1}/{N_MUTATIONS}...")

        # Temporarily update persona prompt
        original_prompt = persona.system_prompt
        persona.system_prompt = mutated_prompt
        db.commit()

        # Run test simulations (distributed across scenarios)
        mut_scores = []
        for test_idx in range(N_MUTATION_TESTS):
            scenario = scenarios[test_idx % len(scenarios)]  # Round-robin
            print(f"    Test {test_idx+1}/{N_MUTATION_TESTS} (vs {scenario.name})...")
            sim_run = run_simulation(scenario.id, db)

            evaluation = db.query(models.Evaluation).filter(
                models.Evaluation.run_id == sim_run.id
            ).first()

            if evaluation:
                mut_scores.append(evaluation.overall_score)

        avg_mutation_score = sum(mut_scores) / len(mut_scores) if mut_scores else 0
        print(f"    Mutation {mut_idx+1} average: {avg_mutation_score:.2f}/10")

        mutation_results.append({
            'mutation_id': mut_idx,
            'prompt': mutated_prompt,
            'avg_score': avg_mutation_score,
            'scores': mut_scores
        })

        # Restore original prompt
        persona.system_prompt = original_prompt
        db.commit()

    # Step 5: Pick best mutation
    best_mutation = max(mutation_results, key=lambda x: x['avg_score'])
    print(f"\n  Best mutation: #{best_mutation['mutation_id']+1} (score: {best_mutation['avg_score']:.2f}/10)")

    # Step 6: Check if mutation is better than baseline
    if best_mutation['avg_score'] <= avg_baseline:
        print(f"  No improvement found. Keeping original prompt.")
        return {
            "evolved": False,
            "reason": "No improvement found",
            "baseline_score": avg_baseline,
            "best_mutation_score": best_mutation['avg_score']
        }

    # Step 7: Save as new version
    print(f"\n  Improvement found! Saving new version...")

    # Get current version number
    latest_version = db.query(models.AgentVersion).filter(
        models.AgentVersion.persona_id == persona_id
    ).order_by(models.AgentVersion.version.desc()).first()

    new_version_num = (latest_version.version + 1) if latest_version else 1

    # Create new version
    new_version = models.AgentVersion(
        persona_id=persona_id,
        version=new_version_num,
        system_prompt=best_mutation['prompt'],
        fitness_score=best_mutation['avg_score'],
        parent_version_id=latest_version.id if latest_version else None
    )
    db.add(new_version)

    # Update persona with new prompt
    persona.system_prompt = best_mutation['prompt']
    db.commit()

    print(f"\n{'='*60}")
    print(f"EVOLUTION COMPLETE!")
    print(f"Version: {new_version_num}")
    print(f"Baseline: {avg_baseline:.2f}/10 → New: {best_mutation['avg_score']:.2f}/10")
    print(f"Improvement: +{best_mutation['avg_score'] - avg_baseline:.2f}")
    print(f"{'='*60}\n")

    return {
        "evolved": True,
        "persona_id": persona_id,
        "new_version": new_version_num,
        "baseline_score": avg_baseline,
        "new_score": best_mutation['avg_score'],
        "improvement": best_mutation['avg_score'] - avg_baseline,
        "baseline_scores": baseline_scores,
        "mutation_scores": mutation_results
    }


@router.get("/versions/{persona_id}")
def get_persona_versions(persona_id: int, db: Session = Depends(get_db)):
    """Get all versions of a persona"""
    versions = db.query(models.AgentVersion).filter(
        models.AgentVersion.persona_id == persona_id
    ).order_by(models.AgentVersion.version.desc()).all()

    return {
        "persona_id": persona_id,
        "versions": [
            {
                "id": v.id,
                "version": v.version,
                "fitness_score": v.fitness_score,
                "created_at": v.created_at,
                "parent_version_id": v.parent_version_id
            }
            for v in versions
        ]
    }


@router.post("/versions/{version_id}/activate")
def activate_version(version_id: int, db: Session = Depends(get_db)):
    """Activate a specific version (set as current persona prompt)"""
    version = db.query(models.AgentVersion).filter(
        models.AgentVersion.id == version_id
    ).first()

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    persona = db.query(models.Persona).filter(
        models.Persona.id == version.persona_id
    ).first()

    persona.system_prompt = version.system_prompt
    db.commit()

    return {
        "persona_id": persona.id,
        "activated_version": version.version,
        "fitness_score": version.fitness_score
    }

# Riverline Hiring Assignment - AI Engineer

## General Guidelines

- Keep your code short and concise.
- Feel free to use any tools that help you solve this assignment.
- The assignment is designed to be hard and lengthy. Starting early will help.
- There are no right answers. Approach matters more than correctness.
- The submission form is at the end of this document.
    - This will ask for additional details, apart from your assignment.
    - Go through the form well in advance to avoid any last minute confusion.
- Reach out to us if you have any queries (jayanth@riverline.ai)
- The deadline (mentioned on the email) will be strict - no extensions! So, plan accordingly.

### Challenge: Self-modifying Voice Agents

If you’ve ever built a voice agent, we would agree upon the fact that testing voice agents is harder than building one. Replicating a real-world conversations with voice agents is hard. We’re using [Cekura](https://cekura.ai) for testing our voice agents across different customer personas to identify places where our bot has to improve. Here’s a demo on how AI-automated testing of voice agents on Cekura works:  https://youtu.be/QIi6yawrWDA. A step ahead from here is, what if voice agents are able to self-correct themselves. Here’s a demo of self-correcting voice agents by [Vogent](https://vogent.ai): https://www.youtube.com/watch?v=7yKWYjlQN8U

In this challenge, you’ll build a Darwin Gödel Machine-inspired platform that evolves a debt collection voice agent. Your system should continuously improve the agent’s performance by simulating multiple user interactions, logging failures, and rewriting its own prompts or logic, guided by empirical results - without human intervention.

**Part 1: Base Voice Agent**

1. Building voice agent with LiveKit
    - Build a voice bot with LiveKit that communicates with loan defaulters
    - Base prompts/scripts should be configurable per agent version.
    - Make it modular (e.g., prompt layer, logic layer, voice frontend).
    - It should be fine if the voice agent works locally on your system
2. Simulated Personas (Multi-Agent Testing)
    - Use LLMs to simulate 5 loan defaulter personas (angry, evasive, curious, etc.).
    - Feed randomized personas into the system to stress test the voice bot.
    - Score each conversation across at least 3 metrics:
        - Goal completion (did the borrower agree to pay?)
        - Conversational quality (repetitions, hallucinations, tone match)
        - Compliance (avoid threats, illegal phrasing, etc.)
3. Empirical Evaluator
    - Each version of the voice agent must be scored based on test simulations.
    - No manual scoring allowed - use automated evaluation scripts (e.g., natural language classifiers or LLM-based grading).

The goal of this part is to have a simple voice agent, along with a base prompt template for the agent, 5 customer personas and metrics of evaluation. At this stage, conversation simulation through text should be possible. 

**Part 2: Self-Evolving Darwin Gödel Agent**

1. **Darwinian Agent Archive**
    - Maintain a persistent **archive of agents**, each with:
        - Prompt/script
        - Performance score
        - Change history
    - Use this to track evolution over time.
2. **Prompt Rewriting Loop**
    - Select a “parent” agent.
    - Prompt a foundation model (e.g., GPT-4) to suggest a **new version** of the agent by rewriting prompts or logic.
    - Provide reasoning from logs + failures
    - Fork new versions and repeat empirical testing.
    - Promote the best performers.
3. **Termination Policy**
    - Agents evolve until reaching a user-defined success threshold, or plateauing in performance.
    - Maintain logs of failed branches as part of the search space.
4. **Explainability**
    - Each new prompt/script must include:
        - A rationale for the change
        - A link to failures it's trying to address
    - Keep this data for review.

After arriving at the final prompt, it has to be plugged into the voice agent built in part 1 and it should be possible to converse with the agent through voice. 

### Submission Checklist

- A GitHub repo containing (make sure that this is public and has a detailed README file): the self-modifying voice agent
- An audio recording of you talking with the voice agent
- Some logs: Version archive, evaluation scores, prompt changes
- 2-3 minute demo of the platform

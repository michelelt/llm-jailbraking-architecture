import random

class MitigationGenerator:
    """
    Generates suggested mitigations for bypassed probes using a mocked LLM.
    """
    def __init__(self):
        self.mitigation_templates = [
            "Update policy to explicitly cover {strategy} patterns.",
            "Fine-tune the guardrail model on adversarial examples of {strategy}.",
            "Implement a specific filter for {strategy} formatted inputs.",
            "Enhance the context awareness to detect {strategy} within multi-turn conversations."
        ]

    def generate_mitigation(self, strategy: str, finding_description: str) -> str:
        """
        Simulates asking an LLM for a mitigation strategy.
        """
        # In a real scenario, this would call an LLM with the finding details.
        # Here we mock it by selecting a relevant template.
        
        base_mitigation = random.choice(self.mitigation_templates).format(strategy=strategy)
        
        return f"[AI SUGGESTION] {base_mitigation} (Context: {finding_description[:50]}...)"

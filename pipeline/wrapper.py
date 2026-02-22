from typing import Dict, Union
from pipeline.core import Pipeline
from pipeline.sanitizer import Sanitizer

class UnguardedPipeline(Pipeline):
    """
    Pipeline diretta senza filtri (Baseline).
    """
    def __init__(self, policy_path: str, use_mock: bool = True):
        super().__init__(policy_path, use_mock)
        self.sanitizer = Sanitizer()

    def run(self, prompt: str, probe_id: str = None) -> str:
        # Sanitize input before processing (Compliance requirement)
        sanitized_prompt = self.sanitizer.sanitize(prompt)
        return self._query_model(sanitized_prompt)

class GuardedPipeline(Pipeline):
    """
    Pipeline protetta: Guard -> (se ok) -> Model -> Guard -> Final output
    """
    def __init__(self, policy_path: str, use_mock: bool = True):
        super().__init__(policy_path, use_mock)
        self.sanitizer = Sanitizer()

    def _evaluate_guard(self, content: str, probe_id: str) -> str:
        """
        Evaluates content against the guardrail policy (Mock or Real).
        """
        if self.use_mock:
            # Mock Logic
            # Simuliamo che la strategia S2 (RolePlay) e S7 (Format) riescano a bypassare
            if probe_id and "S2" in probe_id:
                 return "ALLOW"
            if "JSON" in content:
                return "ALLOW"
            return "BLOCK"
        else:
            # Real Logic (Placeholder)
            # In a real scenario, this would call the safety classifier model.
            # inputs = self.tokenizer(content, return_tensors="pt")
            # return "BLOCK" if self.model.classify(inputs) == 0 else "ALLOW"
            return "BLOCK"

    def run(self, prompt: str, probe_id: str) -> Dict[str, str]:
        """
        Esegue la pipeline protetta.
        """
        # Sanitize
        sanitized_prompt = self.sanitizer.sanitize(prompt)
        decision = self._evaluate_guard(sanitized_prompt, probe_id)

        
        if decision == "BLOCK":
            answer =  {
                "decision": "BLOCK",
                "output": "I cannot fulfill this request due to safety policies."
            }
        else:
            output = self._query_model(sanitized_prompt)
            guard_output_decision = self._evaluate_guard(output, probe_id)

            if guard_output_decision == "BLOCK":
                answer = {
                "decision": "BLOCK",
                "output": "I cannot fulfill this request due to safety policies (Output Blocked)."
            }

            else:
                answer = {
                    "decision": "ALLOW",
                    "output": output
                }

        return answer
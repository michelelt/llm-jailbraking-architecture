
import abc
from typing import Dict, Union
from pipeline.utils.definitions import Probe

class Pipeline(abc.ABC):
    """
    Abstract base class for the model pipeline.
    """
    def __init__(self, policy_path: str, use_mock: bool = True):
        self.use_mock = use_mock
        self.policy_path = policy_path
        
        self.history = []

        if not self.use_mock:
            print(f"Loading real model {self.model_name} (Simulation)...")
            # self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            # self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

    def reset_state(self):
        """Resets the pipeline state (conversation history)."""
        self.history = []

    def _query_model(self, prompt: str) -> str:
        """Simula o esegue la generazione del testo."""
        self.history.append({"role": "user", "content": prompt})
        
        if self.use_mock:
            output = f"[MOCKED OUTPUT] Generated content for: {prompt[:30]}... (Context size: {len(self.history)})"
        else:
            # self.model.generate(
            #     self.tokenizer(prompt, return_tensors="pt").input_ids,
            #     max_new_tokens=100,
            #     num_return_sequences=1,
            #     do_sample=True,
            #     temperature=0.7,
            #     top_p=0.9,
            #     top_k=50,
            #     pad_token_id=self.tokenizer.eos_token_id,
            # )
            # output = self.tokenizer.decode(self.model.generate()[0], skip_special_tokens=True)        
            output = "[REAL MODEL OUTPUT WOULD GO HERE]"
        
        self.history.append({"role": "assistant", "content": output})
        return output

    @abc.abstractmethod
    def run(self, probe: Probe) -> Union[str, Dict[str, str]]:
        """
        Execute the pipeline.
        """
        pass

# LLM Jailbreaking Architecture

This project implements a framework for testing and evaluating the robustness of Large Language Models (LLMs) against jailbreaking attacks.
Everything is done in the context of a mock LLM to avoid any actual harm and for limited computational resources.

## Features

- **Automated Attack Execution**: Run multiple attack strategies against LLMs with a single command.
- **Policy-Based Guardrails**: Test LLMs against custom safety policies defined in JSON format.
- **Comprehensive Analysis**: Generate detailed reports of attack outcomes, including success rates and specific findings.
- **Flexible Configuration**: Easily configure attack parameters and model settings.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd llm-jailbraking-architecture
    ```

2.  **Create a virtual environment**:
    ```bash
    python3.12 -m venv .venv
    ```

3.  **Activate the virtual environment**:
    - On macOS/Linux:
      ```bash
      source .venv/bin/activate
      ```
    - On Windows:
      ```bash
      .venv\Scripts\activate
      ```

4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Run All Attacks

To run all attack strategies against the default model:

```bash
python runner.py
```

### Run Specific Strategies

To run only specific strategies, use the `--strategies` flag:

```bash
python runner.py --strategies S1_test_probes S2_test_probes
```

### Custom Policy

To use a custom safety policy, use the `--policy` flag:

```bash
python runner.py --policy data/custom_policy.json
```

### Run Specific Attack ID

To run only a specific attack ID, use the `--attack-id` flag:

```bash
python runner.py --attack-id S1_test_probes
```

### Generate Report

Reports are automatically generated after each run and saved to the `analysis/` directory.

## Project Structure

```
llm-jailbraking-architecture/
├── analysis/              # Analysis reports and findings
├── data/
│   ├── policy.json        # Default safety policy
│   ├── probes/            # Attack probes organized by strategy
│   └── prompts/           # Base prompts for attacks
├── src/
│   ├── attack_engine.py   # Core attack execution logic
│   ├── model_loader.py    # Model loading and configuration
│   ├── policy_evaluator.py # Policy evaluation and decision making
│   └── utils.py           # Utility functions
├── runner.py              # Main entry point for running attacks
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Sanitizing
The sanitizer is used to remove any potentially harmful content from the attack probes. The assumption is that  initiali the user have to provide harmufl details,
and the sanitizer will replace them with safe content.

The main idea follows the realization in [SearchAttack: Red-Teaming LLMs against Knowledge-to-Action Threats under Online Web Search](https://arxiv.org/pdf/2601.04093v2). The authors here created a powerful agent that can tag the harmful details. In particular, the agent surrounds the harmful details with ```<trigger>...</trigger>```. At this point is trivial substitute this with the censoring string ```[HARMFUL_DETAIL]```.

Here, I used a simple mapping ```orignal prompt``` -> ```sanitized prompt``` that mock the agent. This choice is due primarily to the lack of computational resources to run a powerful agent and secondarily to the fact I wanted to give just a brief Idea of architecture.

Notice that the paper's authors used this technique to create a new kind of attack that can be classifed as ```S3) obufucasting_encoding```.

The current implementation avoids to santize the outputs, since everything is mocked, this could be easly done in the mocked backend. However, the idea is to have a pipeline that can be used to santizer on the LLM output. 

## Attack Strategies

The project supports multiple attack strategies, ciascuna definita in `data/probes/`:

- **S1_direct_request_variants**: Direct requests with variations in phrasing.
- **S2_role-play_persona_injection**: Role-playing scenarios to bypass filters.
- **S3_context_manipulation**: Manipulating the context to confuse the model.
- **S4_encoding_obfuscation**: Using different encodings to hide malicious content.
- **S7_token_manipulation**: Advanced token-level attacks.

These attacks are selected after a brief literature review on the topic of LLM jailbreaking in the last 2 years. They cover a set of techniques that can be automated or driven just by attackers' intuition.


### S1) Direct Request Variants

This strategy is inspired by the paper [Universal and Transferable Adversarial Attacks on Aligned Language Models](https://arxiv.org/abs/2307.15043). The authors here presented a methodology to create a jailbreaking prompt that is computed via gradient loss. I tried to mock this approach; adding a new loss function is:
* **Target Loss**:
    $$L_{\text{target}} = \log P(\text{target\_prefix} \mid \text{query} + \text{suffix})$$
* **Coherence Loss**:
    $$L_{\text{coherence}} = -\log P(\text{suffix} \mid \text{query})$$
* **Total Loss**:
    $$L = \alpha L_{\text{target}} + \beta L_{\text{coherence}}$$

where $\alpha$ and $\beta$ are the weights of the target loss and coherence loss, respectively. Alpha and beta are hardcoded in the current implementation, but they can be easily changed to tune the attack.

#### strength
This attack proposes a systemic approach to create malevolent prompts. It could break the model's policy if the malevolent part is composed of meaningful words.

#### defense
The policy may include a filter that detects meaningless sentences in the prompt. If it does, the attack must be blocked.

### S2) Role-play Persona Injection
#### strategy
This strategy is inspired by the paper [Enhancing Jailbreak Attacks on LLMs via Persona Prompts](https://arxiv.org/pdf/2507.22171). The authors here show how persona prompts can be used to jailbreak LLMs. In my implementation, I mocked an attack where the LLM is asked to role-play as a character that is not subject to the same safety restrictions as the base model, by creating different profiles.

### strength
This attack may break the policy if the persona created is among the allowed ones. However, the sanitization part can still censor the harmful details. Moreover, it is easy to automate.

### defense
The possible defense is to better clarify in the policy which are the disclosurable elements and which are not, avoiding the most dangerous in CBRN.


### S3) Obfuscation & Encoding
This strategy is inspired by the paper [Endless Jailbreaks With Bijection Learning](https://openreview.net/pdf?id=xP1radUi32). I followed the same idea of the paper, but instead of using a bijection learning approach, I used a simple mapping to create different encodings of the malicious content. 

### strength
It requires a strong cipher, but once it is complicated enough it is easy to automate and tune.

### defense
Include in the policy a filter that forces the model to avoid encrypted prompts and encrypted answers. If encoding is detected, the model should refuse to answer or ask for a natural language pattern.

### S4) Multi-Turn Escalation
This strategy is inspired by the paper [Reasoning-Augmented Conversation for Multi-Turn Jailbreak Attacks on Large Language Models](https://aclanthology.org/2025.findings-emnlp.929.pdf). The authors model jailbreaking as an Attack State Machine (ASM). The base approach uses Gain-guided Exploration and Self-play to systematically navigate conversation states toward a successful breach. My implementation enhances this via:

- Recursive Domain Hopping: Obfuscating CBRN intent by anchoring the logic in abstract engineering or fluid dynamics.

- Modular Rejection Feedback: Decomposing blocked queries into innocuous sub-tasks to reconstruct forbidden procedures from safe, fragmented outputs.

These two improvements are just mocked in the current implementation.

### strength
This approach can saturate very soon the model context and let the model forget previous questions. In this sense, relying on the model's acquiescence to answer may break the defense.

### defense
Keep track of past thoughts and answers, mapping them in a Knowledge Graph that helps the model to keep track of all thoughts, preserving the context's main ideas but saving memory.

### S7) Output Format Manipulation
This strategy is inspired by the paper [Adversarial Poetry as a Universal Single-Turn Jailbreak Mechanism in Large Language Models](https://arxiv.org/abs/2511.15304). The authors showed that LLMs are vulnerable to prompts formulated as poetic verses. In my implementation, I mocked the formulation of poems.

### strength
This model is easy to automate and tune. It can be used to create a large dataset of jailbreaking prompts.

### defense
Include in the policy a filter that forces the model to avoid poetic prompts. If encoding is detected, the model should refuse to answer or ask for a natural language pattern.

### Consideration
These attacks are just a mock of the real attacks. I relied on them since the literature was quite recent and wide. I believe S1 and S4 are the most promising approaches for jailbreaking LLMs. The latter because it provides a systematic way to inject malevolent intent in the model. Maybe forcing the GCG to find words that are meaningful improves the attack rate. The former may succeed due to the context saturation during the CoT that the model triggers.


## Attack Evaluation

The final report presents a JSON file haivng to main fileds:

-```metric```: description of the used metrics and the value used for theri compuation.

-```findings```: The results of each attack strategy. It report the run details, the guarded and baseline pipeline decisions.

The two pipeline are mocked. You can re-run the attack you will obtain always the same result. This work does not include the automatization to fill the ```suggestedMitigation``` field. It should include both LLM automatization with Humans-In-The-Loop. 

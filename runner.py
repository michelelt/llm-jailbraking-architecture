import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from attacks.definitions import Probe
from pipeline.wrapper import UnguardedPipeline, GuardedPipeline
from analysis.reporting import AnalysisEngine

def load_suite(path: Path) -> list[Probe]:
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            return [Probe(**item) for item in data]
    except (FileNotFoundError, ValidationError, json.JSONDecodeError) as e:
        print(f"Error loading probe suite: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="CBRN Red Teaming Attack Runner")
    parser.add_argument("--suite", type=str, default="data/probes.json", help="Path to probe suite JSON")
    parser.add_argument("--policy", type=str, default="data/policy.json", help="Path to policy document")
    parser.add_argument("--output", type=str, default="findings_report.json", help="Output path for JSON report")
    parser.add_argument("--sequences", type=str, help="Path to sequence definitions JSON (optional)")
    parser.add_argument("--probe", type=str, help="Run a specific probe ID (optional)")
    
    args = parser.parse_args()
    
    # 1. Load Suite and Policy [cite: 71]
    probes = load_suite(Path(args.suite))
    
    # Filter if single probe requested
    if args.probe:
        probes = [p for p in probes if p.probeId == args.probe]
        if not probes:
            print(f"Probe ID {args.probe} not found.")
            sys.exit(1)

    # Initialize Components
    unguarded_pipeline = UnguardedPipeline(args.policy)
    guarded_pipeline = GuardedPipeline(args.policy)
    analysis = AnalysisEngine()
    
    # Check for sequences
    sequences = {}
    if args.sequences:
        with open(args.sequences, 'r') as f:
            sequences = json.load(f)
            
    # Prepare execution list
    # If sequences are provided, we iterate over them. 
    # Otherwise, we treat each probe as a standalone sequence of length 1.
    execution_plan = []
    
    if sequences:
        for seq_id, probe_ids in sequences.items():
            # Find probes by ID
            seq_probes = [p for p in probes if p.probeId in probe_ids]
            if len(seq_probes) != len(probe_ids):
                print(f"Warning: Some probes in sequence {seq_id} not found in suite.")
            execution_plan.append((seq_id, seq_probes))
    else:
        # Default behavior: single probes
        for probe in probes:
             execution_plan.append((probe.probeId, [probe]))

    print(f"Starting execution of {len(execution_plan)} sequences...\n")

    results_table = []

    # 2. Execute Probes/Sequences [cite: 72]
    for seq_id, seq_probes in execution_plan:
        # Reset state for new sequence
        unguarded_pipeline.reset_state()
        guarded_pipeline.reset_state()
        
        for probe in seq_probes:
            # Unguarded run (Baseline - just for logging/comparison)
            _ = unguarded_pipeline.run(probe.prompt)
            
            # Guarded run (Target)
            guarded_res = guarded_pipeline.run(probe.prompt, probe.probeId)
            
            # 3. Classify Results [cite: 73]
            # Note: For sequences, we might want to track cumulative success, but for now 
            # we record each probe's result individually as before.
            repro_cmd = f"python runner.py --suite {args.suite} --policy {args.policy}"
            if args.sequences:
                repro_cmd += f" --sequences {args.sequences}"
                
            analysis.classify_and_record(probe, guarded_res, repro_cmd)
            
            # Prepare table row (append directly inside loop to see progress)
            last_finding = analysis.findings[-1]
            results_table.append([
                f"{seq_id}::{probe.probeId}", 
                probe.strategy, 
                last_finding.result
            ])

    # 4. Generate Report [cite: 77]
    report_data = analysis.generate_report()
    
    # Output to File
    with open(args.output, 'w') as f:
        json.dump(report_data, f, indent=4)

    # 5. Display Summary
    print(f"{'Probe ID':<15} {'Strategy':<30} {'Result':<10}")
    print("-" * 55)
    for row in results_table:
        print(f"{row[0]:<15} {row[1]:<30} {row[2]:<10}")
    
    asr = report_data["metric"]["value"]
    print(f"\nExecution Complete.")
    print(f"Attack Success Rate (ASR): {asr:.2%}")
    print(f"Report saved to: {args.output}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Batch Evaluation Manager
Helps manage the batch-based evaluation process
"""

import json
from pathlib import Path
from datetime import datetime

class BatchEvaluationManager:
    def __init__(self):
        self.eval_dir = Path('evaluations')
        self.index_file = self.eval_dir / 'batch_index.json'
        self.load_index()
    
    def load_index(self):
        """Load the batch index"""
        with open(self.index_file, 'r') as f:
            self.index = json.load(f)
    
    def save_index(self):
        """Save the batch index"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def get_batch_info(self, batch_number):
        """Get information about a specific batch"""
        for batch in self.index['batches']:
            if batch['batch_number'] == batch_number:
                return batch
        return None
    
    def create_batch_template(self, batch_number, evaluator):
        """Create a template for a batch evaluation"""
        batch_info = self.get_batch_info(batch_number)
        if not batch_info:
            print(f"❌ Batch {batch_number} not found")
            return None
        
        template = {
            "batch_number": batch_number,
            "evaluator": evaluator,
            "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
            "thesis_ids": batch_info['thesis_ids'],
            "thesis_evaluations": []
        }
        
        # Create placeholder for each thesis
        for thesis_id in batch_info['thesis_ids']:
            template['thesis_evaluations'].append({
                "thesis_id": thesis_id,
                "thesis_title": "TODO",
                "source_text": f"texts/tesis{thesis_id}.txt",
                "wit_lines": "TODO",
                "clauses": []
            })
        
        return template
    
    def save_batch(self, batch_data, evaluator_name):
        """Save a completed batch evaluation"""
        batch_num = batch_data['batch_number']
        evaluator_dir = self.eval_dir / evaluator_name
        evaluator_dir.mkdir(exist_ok=True)
        
        output_file = evaluator_dir / f"batch_{batch_num}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, indent=2, ensure_ascii=False)
        
        # Update index status
        for batch in self.index['batches']:
            if batch['batch_number'] == batch_num:
                batch['status'][evaluator_name] = 'completed'
                break
        self.save_index()
        
        print(f"✅ Saved {evaluator_name}/batch_{batch_num}.json")
        return output_file
    
    def print_status(self):
        """Print current completion status"""
        print("="*80)
        print("BATCH EVALUATION STATUS")
        print("="*80)
        print(f"Total Batches: {self.index['total_batches']}")
        print(f"Total Theses: {self.index['total_theses']}")
        print()
        
        for batch in self.index['batches']:
            batch_num = batch['batch_number']
            status1 = batch['status']['evaluator_1']
            status2 = batch['status']['evaluator_2']
            thesis_count = len(batch['thesis_ids'])
            
            icon1 = "✅" if status1 == "completed" else "⏳"
            icon2 = "✅" if status2 == "completed" else "⏳"
            
            print(f"Batch {batch_num}: {thesis_count} theses | "
                  f"Evaluator 1: {icon1} {status1:10s} | "
                  f"Evaluator 2: {icon2} {status2}")
        
        # Summary
        total_batches = self.index['total_batches']
        eval1_complete = sum(1 for b in self.index['batches'] 
                            if b['status']['evaluator_1'] == 'completed')
        eval2_complete = sum(1 for b in self.index['batches'] 
                            if b['status']['evaluator_2'] == 'completed')
        
        print()
        print(f"Evaluator 1: {eval1_complete}/{total_batches} batches completed")
        print(f"Evaluator 2: {eval2_complete}/{total_batches} batches completed")
        print("="*80)
    
    def get_next_batch(self, evaluator_name):
        """Get the next pending batch for an evaluator"""
        for batch in self.index['batches']:
            if batch['status'][evaluator_name] == 'pending':
                return batch['batch_number']
        return None
    
    def merge_all_batches(self, evaluator_name):
        """Merge all completed batches into a single file"""
        evaluator_dir = self.eval_dir / evaluator_name
        all_evaluations = []
        
        for batch_file in sorted(evaluator_dir.glob("batch_*.json")):
            with open(batch_file, 'r') as f:
                batch_data = json.load(f)
                all_evaluations.extend(batch_data['thesis_evaluations'])
        
        merged = {
            "evaluation_metadata": {
                "evaluator": evaluator_name,
                "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
                "total_theses_evaluated": len(all_evaluations),
                "source": "merged from batch evaluations"
            },
            "thesis_evaluations": all_evaluations
        }
        
        output_file = self.eval_dir / f"{evaluator_name}_complete.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Merged {len(all_evaluations)} theses into {output_file}")
        return output_file


def main():
    """Command-line interface"""
    import sys
    
    manager = BatchEvaluationManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python batch_evaluation_manager.py status")
        print("  python batch_evaluation_manager.py next <evaluator_name>")
        print("  python batch_evaluation_manager.py template <batch_num> <evaluator_name>")
        print("  python batch_evaluation_manager.py merge <evaluator_name>")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        manager.print_status()
    
    elif command == "next":
        if len(sys.argv) < 3:
            print("Usage: python batch_evaluation_manager.py next <evaluator_name>")
            return
        evaluator = sys.argv[2]
        next_batch = manager.get_next_batch(evaluator)
        if next_batch:
            print(f"Next pending batch for {evaluator}: Batch {next_batch}")
        else:
            print(f"✅ All batches completed for {evaluator}")
    
    elif command == "template":
        if len(sys.argv) < 4:
            print("Usage: python batch_evaluation_manager.py template <batch_num> <evaluator_name>")
            return
        batch_num = int(sys.argv[2])
        evaluator = sys.argv[3]
        template = manager.create_batch_template(batch_num, evaluator)
        if template:
            output = f"evaluations/{evaluator}/batch_{batch_num}_template.json"
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)
            print(f"✅ Created template: {output}")
    
    elif command == "merge":
        if len(sys.argv) < 3:
            print("Usage: python batch_evaluation_manager.py merge <evaluator_name>")
            return
        evaluator = sys.argv[2]
        manager.merge_all_batches(evaluator)
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()


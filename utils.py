import json
import csv
import os

def export_results(results, export_format, output_file):
    """
    Exports scan results to the specified format.
    results: list of dicts [{'port': int, 'status': str, 'service': str}]
    """
    if not results:
        return
        
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    if export_format == 'json':
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)
    elif export_format == 'csv':
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['port', 'status', 'service'])
            writer.writeheader()
            writer.writerows(results)
    elif export_format == 'txt':
        with open(output_file, 'w') as f:
            f.write(f"{'PORT':<10} {'STATUS':<15} {'SERVICE'}\n")
            f.write("-" * 40 + "\n")
            for res in results:
                f.write(f"{res['port']:<10} {res['status']:<15} {res['service']}\n")

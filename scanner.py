import argparse
import time
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from port_scanner import PortScanner
from utils import export_results
from services import COMMON_PORTS

console = Console()

def parse_ports(port_arg):
    ports = []
    if '-' in port_arg:
        start, end = map(int, port_arg.split('-'))
        ports = list(range(start, end + 1))
    elif ',' in port_arg:
        ports = [int(p) for p in port_arg.split(',')]
    else:
        ports = [int(port_arg)]
    return ports

def main():
    parser = argparse.ArgumentParser(description="Advanced Python Port Scanner")
    parser.add_argument("target", help="Target IP or Domain (e.g., example.com)")
    parser.add_argument("-p", "--ports", help="Port range (e.g., 80 or 1-1000 or 22,80,443)")
    parser.add_argument("--common", action="store_true", help="Scan common ports")
    parser.add_argument("--threads", type=int, default=100, help="Number of threads (default: 100)")
    parser.add_argument("--timeout", type=float, default=1.0, help="Socket timeout in seconds (default: 1.0)")
    parser.add_argument("--output", help="Save scan results to file (e.g., results.json)")

    args = parser.parse_args()

    # Determine ports to scan
    if args.common:
        ports_to_scan = list(COMMON_PORTS.keys())
    elif args.ports:
        try:
            ports_to_scan = parse_ports(args.ports)
        except ValueError:
            console.print("[bold red]Invalid port format. Use 80, 1-1000, or 22,80,443[/bold red]")
            sys.exit(1)
    else:
        console.print("[bold red]Please specify ports to scan using -p or --common flag.[/bold red]")
        sys.exit(1)

    scanner = PortScanner(args.target, ports_to_scan, args.timeout, args.threads)

    if not scanner.target_ip:
        console.print(f"[bold red]Failed to resolve hostname: {args.target}[/bold red]")
        sys.exit(1)

    console.print(f"\nTarget: [bold cyan]{args.target}[/bold cyan]")
    console.print(f"IP: [bold cyan]{scanner.target_ip}[/bold cyan]\n")
    
    start_time = time.time()
    
    with Progress() as progress:
        task = progress.add_task("[green]Scanning ports...", total=len(ports_to_scan))
        def update_progress():
            progress.update(task, advance=1)
        
        scanner.run(progress_callback=update_progress)
        
    end_time = time.time()
    duration = end_time - start_time

    # Display Results in a rich Table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("PORT", style="dim", width=12)
    table.add_column("STATUS", width=15)
    table.add_column("SERVICE", justify="right")

    for res in scanner.results:
        status_color = "green" if res['status'] == 'OPEN' else "red" if res['status'] == 'CLOSED' else "yellow"
        table.add_row(
            str(res['port']),
            f"[{status_color}]{res['status']}[/]",
            res['service']
        )
    
    console.print("\n")
    console.print(table)
    console.print(f"\nScan completed in [bold green]{duration:.2f}[/bold green] seconds\n")

    # Handle Export
    if args.output:
        ext = args.output.split('.')[-1].lower()
        if ext not in ['json', 'csv', 'txt']:
            console.print("[bold yellow]Unsupported output format. Use .json, .csv, or .txt. Defaulting to .json[/bold yellow]")
            ext = 'json'
            args.output = f"{args.output}.json"
            
        # Ensure output is saved to results/ directory if not explicitly provided
        if not os.path.dirname(args.output):
            args.output = os.path.join("results", args.output)
            
        export_results(scanner.results, ext, args.output)
        console.print(f"Results exported to [bold cyan]{args.output}[/bold cyan]\n")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Multi-Agent Industrial Monitoring System
Main entry point for command-line execution
"""

import argparse
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_analysis(data_path: str, api_key: str = None, 
                 enable_reasoning: bool = True,
                 enable_debate: bool = True,
                 enable_planning: bool = True,
                 verbose: bool = True) -> dict:
    """
    Run the multi-agent analysis pipeline on data.
    
    Args:
        data_path: Path to CSV data file
        api_key: Gemini API key (optional, uses fallback mode if not provided)
        enable_reasoning: Enable Chain-of-Thought reasoning
        enable_debate: Enable multi-perspective debate
        enable_planning: Enable strategic planning
        verbose: Print progress messages
        
    Returns:
        Analysis results dictionary
    """
    from orchestrator import SystemOrchestrator
    
    def progress_callback(stage, progress, message):
        if verbose:
            print(f"[{progress:3d}%] {stage}: {message}")
    
    # Initialize orchestrator
    if verbose:
        print("\n" + "=" * 60)
        print("🏭 MULTI-AGENT INDUSTRIAL MONITORING SYSTEM")
        print("=" * 60)
        print(f"\n📂 Data: {data_path}")
        print(f"🔑 API Key: {'Provided' if api_key else 'Not provided (fallback mode)'}")
        print(f"🧠 Reasoning: {'Enabled' if enable_reasoning else 'Disabled'}")
        print(f"🎭 Debate: {'Enabled' if enable_debate else 'Disabled'}")
        print(f"📋 Planning: {'Enabled' if enable_planning else 'Disabled'}")
        print("\n" + "-" * 60 + "\n")
    
    orchestrator = SystemOrchestrator(api_key=api_key)
    
    # Run pipeline
    result = orchestrator.run_pipeline(
        data_path,
        enable_reasoning=enable_reasoning,
        enable_debate=enable_debate,
        enable_planning=enable_planning,
        progress_callback=progress_callback if verbose else None
    )
    
    if verbose:
        print("\n" + "-" * 60)
        if result['status'] == 'success':
            print("\n✅ ANALYSIS COMPLETED SUCCESSFULLY!")
            print(f"\n📊 Key Statistics:")
            print(f"   • Machines analyzed: {result.get('row_count', 'N/A')}")
            print(f"   • Anomalies detected: {result.get('anomaly_count', 'N/A')}")
            print(f"   • Decisions generated: {len(result.get('decisions', {}).get('decisions', []))}")
            print(f"   • Pipeline stages: {len(result.get('stages_completed', []))}")
            
            # Save report
            if 'report' in result:
                report_path = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(result['report'])
                print(f"\n📄 Report saved to: {report_path}")
        else:
            print("\n❌ ANALYSIS FAILED!")
            print(f"   Errors: {result.get('errors', [])}")
        
        print("\n" + "=" * 60 + "\n")
    
    return result


def run_streamlit():
    """Launch the Streamlit web interface."""
    import subprocess
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    subprocess.run(["streamlit", "run", app_path])


def generate_sample():
    """Generate sample data for testing."""
    from sample_data import save_sample_data
    save_sample_data("sample_industrial_data.csv", n_machines=75)


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Industrial Monitoring System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run analysis on data file
  python main.py analyze --data machine_data.csv --api-key YOUR_KEY
  
  # Generate sample data
  python main.py sample
  
  # Launch web interface
  python main.py web
  
  # Run with all features disabled (fast mode)
  python main.py analyze --data data.csv --no-reasoning --no-debate --no-planning
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run analysis on data')
    analyze_parser.add_argument('--data', '-d', required=True, help='Path to CSV data file')
    analyze_parser.add_argument('--api-key', '-k', help='Gemini API key', default=os.environ.get('GEMINI_API_KEY'))
    analyze_parser.add_argument('--no-reasoning', action='store_true', help='Disable Chain-of-Thought reasoning')
    analyze_parser.add_argument('--no-debate', action='store_true', help='Disable multi-perspective debate')
    analyze_parser.add_argument('--no-planning', action='store_true', help='Disable strategic planning')
    analyze_parser.add_argument('--quiet', '-q', action='store_true', help='Suppress progress output')
    
    # Web command
    subparsers.add_parser('web', help='Launch Streamlit web interface')
    
    # Sample command
    subparsers.add_parser('sample', help='Generate sample data for testing')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        if not os.path.exists(args.data):
            print(f"❌ Error: File not found: {args.data}")
            sys.exit(1)
        
        result = run_analysis(
            data_path=args.data,
            api_key=args.api_key,
            enable_reasoning=not args.no_reasoning,
            enable_debate=not args.no_debate,
            enable_planning=not args.no_planning,
            verbose=not args.quiet
        )
        
        sys.exit(0 if result['status'] == 'success' else 1)
    
    elif args.command == 'web':
        run_streamlit()
    
    elif args.command == 'sample':
        generate_sample()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Edit Data Comparison Script
Processes and compares raw vs normalized edit data from JSON files

This script loads two JSON files containing edit data:
- raw_edits.json: Original, unnormalized edit data
- normalized_edits.json: Processed and normalized edit data

It then outputs a comparison showing:
- List of edits
- Edit sizes (byte changes)
- Timestamps
- Normalization differences
"""

import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import argparse
from pathlib import Path


class EditDataProcessor:
    """Process and compare edit data from JSON files"""
    
    def __init__(self, raw_file: str, normalized_file: str):
        """
        Initialize processor with file paths
        
        Args:
            raw_file: Path to raw edit data JSON file
            normalized_file: Path to normalized edit data JSON file
        """
        self.raw_file = Path(raw_file)
        self.normalized_file = Path(normalized_file)
        self.raw_data = None
        self.normalized_data = None
    
    def load_data(self) -> bool:
        """
        Load JSON data from both files
        
        Returns:
            bool: True if both files loaded successfully
        """
        try:
            # Load raw data
            if self.raw_file.exists():
                with open(self.raw_file, 'r', encoding='utf-8') as f:
                    self.raw_data = json.load(f)
                print(f"✓ Loaded raw data from: {self.raw_file}")
            else:
                print(f"✗ Raw data file not found: {self.raw_file}")
                return False
            
            # Load normalized data
            if self.normalized_file.exists():
                with open(self.normalized_file, 'r', encoding='utf-8') as f:
                    self.normalized_data = json.load(f)
                print(f"✓ Loaded normalized data from: {self.normalized_file}")
            else:
                print(f"✗ Normalized data file not found: {self.normalized_file}")
                return False
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"✗ JSON parsing error: {e}")
            return False
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            return False
    
    def generate_sample_data(self):
        """Generate sample edit data for demonstration"""
        print("Generating sample data for demonstration...")
        
        # Sample raw edit data (as might come from Wikipedia API)
        raw_data = {
            "query": {
                "pages": {
                    "12345": {
                        "pageid": 12345,
                        "title": "Machine Learning",
                        "revisions": [
                            {
                                "revid": 987654321,
                                "parentid": 987654320,
                                "user": "DataScientist_John",
                                "userid": 12345,
                                "timestamp": "2023-12-01T14:30:00Z",
                                "size": 15420,
                                "sizediff": 342,
                                "comment": "Added section on neural networks",
                                "contentformat": "text/x-wiki",
                                "contentmodel": "wikitext",
                                "tags": ["mobile web edit"]
                            },
                            {
                                "revid": 987654322,
                                "parentid": 987654321,
                                "user": "WikiGardener_Alice",
                                "userid": 12346,
                                "timestamp": "2023-12-01T15:45:00Z",
                                "size": 15398,
                                "sizediff": -22,
                                "comment": "Fixed typos and grammar",
                                "contentformat": "text/x-wiki",
                                "contentmodel": "wikitext",
                                "tags": ["minor edit"]
                            },
                            {
                                "revid": 987654323,
                                "parentid": 987654322,
                                "user": "ResearcherBob",
                                "userid": 12347,
                                "timestamp": "2023-12-02T09:15:00Z",
                                "size": 16125,
                                "sizediff": 727,
                                "comment": "Added references and citations",
                                "contentformat": "text/x-wiki",
                                "contentmodel": "wikitext",
                                "tags": []
                            },
                            {
                                "revid": 987654324,
                                "parentid": 987654323,
                                "user": "StudentCarol",
                                "userid": 12348,
                                "timestamp": "2023-12-02T16:20:00Z",
                                "size": 16089,
                                "sizediff": -36,
                                "comment": "Removed duplicate sentence",
                                "contentformat": "text/x-wiki",
                                "contentmodel": "wikitext",
                                "tags": ["newcomer task"]
                            }
                        ]
                    }
                }
            }
        }
        
        # Sample normalized data (processed for analysis)
        normalized_data = {
            "page_id": 12345,
            "page_title": "Machine Learning",
            "total_edits": 4,
            "edit_summary": {
                "total_size_changes": 1011,
                "net_size_change": 1011,
                "average_edit_size": 252.75,
                "additive_edits": 2,
                "maintenance_edits": 2
            },
            "contributors": {
                "DataScientist_John": {
                    "userid": 12345,
                    "edits_count": 1,
                    "total_size_added": 342,
                    "contribution_type": "additive"
                },
                "WikiGardener_Alice": {
                    "userid": 12346,
                    "edits_count": 1,
                    "total_size_added": -22,
                    "contribution_type": "maintenance"
                },
                "ResearcherBob": {
                    "userid": 12347,
                    "edits_count": 1,
                    "total_size_added": 727,
                    "contribution_type": "additive"
                },
                "StudentCarol": {
                    "userid": 12348,
                    "edits_count": 1,
                    "total_size_added": -36,
                    "contribution_type": "maintenance"
                }
            },
            "edits": [
                {
                    "edit_id": "edit_001",
                    "revid": 987654321,
                    "contributor": "DataScientist_John",
                    "contributor_id": 12345,
                    "timestamp": "2023-12-01T14:30:00Z",
                    "timestamp_unix": 1701439800,
                    "size_change": 342,
                    "edit_type": "content_addition",
                    "edit_category": "major_addition",
                    "quality_score": 0.85,
                    "impact_score": 7.2
                },
                {
                    "edit_id": "edit_002",
                    "revid": 987654322,
                    "contributor": "WikiGardener_Alice",
                    "contributor_id": 12346,
                    "timestamp": "2023-12-01T15:45:00Z",
                    "timestamp_unix": 1701444300,
                    "size_change": -22,
                    "edit_type": "maintenance",
                    "edit_category": "correction",
                    "quality_score": 0.95,
                    "impact_score": 3.1
                },
                {
                    "edit_id": "edit_003",
                    "revid": 987654323,
                    "contributor": "ResearcherBob",
                    "contributor_id": 12347,
                    "timestamp": "2023-12-02T09:15:00Z",
                    "timestamp_unix": 1701507300,
                    "size_change": 727,
                    "edit_type": "content_addition",
                    "edit_category": "major_addition",
                    "quality_score": 0.92,
                    "impact_score": 8.7
                },
                {
                    "edit_id": "edit_004",
                    "revid": 987654324,
                    "contributor": "StudentCarol",
                    "contributor_id": 12348,
                    "timestamp": "2023-12-02T16:20:00Z",
                    "timestamp_unix": 1701532800,
                    "size_change": -36,
                    "edit_type": "maintenance",
                    "edit_category": "cleanup",
                    "quality_score": 0.78,
                    "impact_score": 2.4
                }
            ],
            "processing_metadata": {
                "normalization_date": "2023-12-08T10:30:00Z",
                "algorithm_version": "1.2.0",
                "quality_threshold": 0.7,
                "impact_calculation_method": "weighted_contribution"
            }
        }
        
        # Save sample data
        with open(self.raw_file, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=2)
        
        with open(self.normalized_file, 'w', encoding='utf-8') as f:
            json.dump(normalized_data, f, indent=2)
        
        print(f"✓ Generated sample raw data: {self.raw_file}")
        print(f"✓ Generated sample normalized data: {self.normalized_file}")
        
        # Load the generated data
        self.raw_data = raw_data
        self.normalized_data = normalized_data
    
    def extract_raw_edits(self) -> List[Dict[str, Any]]:
        """Extract edit information from raw Wikipedia API data"""
        edits = []
        
        if not self.raw_data or 'query' not in self.raw_data:
            return edits
        
        for page_id, page_data in self.raw_data['query']['pages'].items():
            if 'revisions' in page_data:
                for revision in page_data['revisions']:
                    edit = {
                        'revid': revision.get('revid'),
                        'user': revision.get('user'),
                        'userid': revision.get('userid'),
                        'timestamp': revision.get('timestamp'),
                        'size': revision.get('size'),
                        'size_diff': revision.get('sizediff', 0),
                        'comment': revision.get('comment', ''),
                        'tags': revision.get('tags', [])
                    }
                    edits.append(edit)
        
        return edits
    
    def extract_normalized_edits(self) -> List[Dict[str, Any]]:
        """Extract edit information from normalized data"""
        if not self.normalized_data or 'edits' not in self.normalized_data:
            return []
        
        return self.normalized_data['edits']
    
    def format_timestamp(self, timestamp: str) -> str:
        """Format timestamp for display"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            return timestamp
    
    def print_comparison_header(self):
        """Print formatted header for comparison"""
        print("\n" + "="*80)
        print("EDIT DATA COMPARISON: RAW vs NORMALIZED")
        print("="*80)
    
    def print_raw_data_summary(self):
        """Print summary of raw data"""
        raw_edits = self.extract_raw_edits()
        
        print(f"\n📄 RAW DATA SUMMARY")
        print("-" * 40)
        print(f"Total edits found: {len(raw_edits)}")
        
        if raw_edits:
            total_size_changes = sum(edit['size_diff'] for edit in raw_edits)
            print(f"Total size changes: {total_size_changes:+d} bytes")
            print(f"Contributors: {len(set(edit['user'] for edit in raw_edits))}")
            print(f"Time range: {self.format_timestamp(raw_edits[0]['timestamp'])} to {self.format_timestamp(raw_edits[-1]['timestamp'])}")
        
        print(f"\n📝 RAW EDITS LIST:")
        print("-" * 40)
        for i, edit in enumerate(raw_edits, 1):
            print(f"{i:2d}. {edit['user']} | {self.format_timestamp(edit['timestamp'])} | {edit['size_diff']:+4d} bytes | {edit['comment'][:50]}{'...' if len(edit['comment']) > 50 else ''}")
    
    def print_normalized_data_summary(self):
        """Print summary of normalized data"""
        normalized_edits = self.extract_normalized_edits()
        
        print(f"\n🔧 NORMALIZED DATA SUMMARY")
        print("-" * 40)
        print(f"Total edits processed: {len(normalized_edits)}")
        
        if normalized_edits:
            total_impact = sum(edit['impact_score'] for edit in normalized_edits)
            avg_quality = sum(edit['quality_score'] for edit in normalized_edits) / len(normalized_edits)
            print(f"Total impact score: {total_impact:.1f}")
            print(f"Average quality score: {avg_quality:.2f}")
            
            edit_types = {}
            for edit in normalized_edits:
                edit_type = edit.get('edit_type', 'unknown')
                edit_types[edit_type] = edit_types.get(edit_type, 0) + 1
            
            print(f"Edit type distribution: {dict(edit_types)}")
        
        print(f"\n⚙️  NORMALIZED EDITS LIST:")
        print("-" * 40)
        for i, edit in enumerate(normalized_edits, 1):
            quality_indicator = "⭐" if edit['quality_score'] > 0.9 else "✓" if edit['quality_score'] > 0.8 else "○"
            print(f"{i:2d}. {quality_indicator} {edit['contributor']} | {self.format_timestamp(edit['timestamp'])} | {edit['size_change']:+4d} bytes | Impact: {edit['impact_score']:.1f} | Type: {edit['edit_type']}")
    
    def print_detailed_comparison(self):
        """Print detailed side-by-side comparison"""
        raw_edits = self.extract_raw_edits()
        normalized_edits = self.extract_normalized_edits()
        
        print(f"\n🔍 DETAILED COMPARISON")
        print("-" * 80)
        print(f"{'Raw Data':<35} | {'Normalized Data':<35}")
        print("-" * 35 + " | " + "-" * 35)
        
        max_edits = max(len(raw_edits), len(normalized_edits))
        
        for i in range(max_edits):
            raw_edit = raw_edits[i] if i < len(raw_edits) else None
            norm_edit = normalized_edits[i] if i < len(normalized_edits) else None
            
            if raw_edit:
                raw_line = f"{raw_edit['user'][:15]:<15} {raw_edit['size_diff']:+4d}b"
            else:
                raw_line = " " * 25
            
            if norm_edit:
                norm_line = f"{norm_edit['contributor'][:15]:<15} {norm_edit['size_change']:+4d}b I:{norm_edit['impact_score']:.1f}"
            else:
                norm_line = " " * 30
            
            print(f"{raw_line:<35} | {norm_line:<35}")
    
    def print_statistics_comparison(self):
        """Print statistical comparison"""
        raw_edits = self.extract_raw_edits()
        normalized_edits = self.extract_normalized_edits()
        
        print(f"\n📊 STATISTICS COMPARISON")
        print("-" * 50)
        
        # Size statistics
        raw_sizes = [edit['size_diff'] for edit in raw_edits]
        norm_sizes = [edit['size_change'] for edit in normalized_edits]
        
        if raw_sizes:
            print(f"Size Changes:")
            print(f"  Raw data    - Total: {sum(raw_sizes):+d}, Avg: {sum(raw_sizes)/len(raw_sizes):+.1f}, Range: {min(raw_sizes):+d} to {max(raw_sizes):+d}")
        
        if norm_sizes:
            print(f"  Normalized  - Total: {sum(norm_sizes):+d}, Avg: {sum(norm_sizes)/len(norm_sizes):+.1f}, Range: {min(norm_sizes):+d} to {max(norm_sizes):+d}")
        
        # Time analysis
        if raw_edits:
            raw_timestamps = [edit['timestamp'] for edit in raw_edits]
            print(f"\nTime Range:")
            print(f"  Raw data    - From: {self.format_timestamp(raw_timestamps[0])}")
            print(f"              - To:   {self.format_timestamp(raw_timestamps[-1])}")
        
        if normalized_edits:
            norm_timestamps = [edit['timestamp'] for edit in normalized_edits]
            print(f"  Normalized  - From: {self.format_timestamp(norm_timestamps[0])}")
            print(f"              - To:   {self.format_timestamp(norm_timestamps[-1])}")
        
        # Quality metrics (only available in normalized data)
        if normalized_edits:
            quality_scores = [edit['quality_score'] for edit in normalized_edits]
            impact_scores = [edit['impact_score'] for edit in normalized_edits]
            
            print(f"\nQuality Metrics (Normalized only):")
            print(f"  Quality scores - Avg: {sum(quality_scores)/len(quality_scores):.2f}, Range: {min(quality_scores):.2f} to {max(quality_scores):.2f}")
            print(f"  Impact scores  - Avg: {sum(impact_scores)/len(impact_scores):.1f}, Range: {min(impact_scores):.1f} to {max(impact_scores):.1f}")
    
    def export_comparison_report(self, output_file: str = "edit_comparison_report.txt"):
        """Export detailed comparison to text file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # Redirect print to file temporarily
                original_stdout = sys.stdout
                sys.stdout = f
                
                self.print_comparison_header()
                self.print_raw_data_summary()
                self.print_normalized_data_summary()
                self.print_detailed_comparison()
                self.print_statistics_comparison()
                
                # Restore stdout
                sys.stdout = original_stdout
            
            print(f"\n💾 Comparison report exported to: {output_file}")
            
        except Exception as e:
            print(f"✗ Error exporting report: {e}")
    
    def run_comparison(self, generate_sample: bool = False, export_report: bool = False):
        """
        Run the complete comparison process
        
        Args:
            generate_sample: Whether to generate sample data if files don't exist
            export_report: Whether to export a detailed report to file
        """
        # Try to load existing data first
        if not self.load_data():
            if generate_sample:
                self.generate_sample_data()
            else:
                print("❌ Failed to load data files. Use --generate-sample to create sample data.")
                return False
        
        # Print all comparisons
        self.print_comparison_header()
        self.print_raw_data_summary()
        self.print_normalized_data_summary()
        self.print_detailed_comparison()
        self.print_statistics_comparison()
        
        # Export report if requested
        if export_report:
            self.export_comparison_report()
        
        print(f"\n✅ Comparison completed successfully!")
        return True


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="Compare raw and normalized Wikipedia edit data from JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compare_edit_data.py raw_edits.json normalized_edits.json
  python compare_edit_data.py --generate-sample raw_edits.json normalized_edits.json
  python compare_edit_data.py --export-report raw_edits.json normalized_edits.json
        """
    )
    
    parser.add_argument('raw_file', help='Path to raw edit data JSON file')
    parser.add_argument('normalized_file', help='Path to normalized edit data JSON file')
    parser.add_argument('--generate-sample', action='store_true', 
                       help='Generate sample data if files do not exist')
    parser.add_argument('--export-report', action='store_true',
                       help='Export detailed comparison report to text file')
    
    args = parser.parse_args()
    
    # Create processor and run comparison
    processor = EditDataProcessor(args.raw_file, args.normalized_file)
    success = processor.run_comparison(
        generate_sample=args.generate_sample,
        export_report=args.export_report
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 
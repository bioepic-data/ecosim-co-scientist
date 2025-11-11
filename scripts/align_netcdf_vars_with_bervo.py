#!/usr/bin/env python
"""Align EcoSIM NetCDF variables with BERVO ontology terms."""

import sys
from pathlib import Path
import pandas as pd


def load_netcdf_vars(tsv_file: Path) -> pd.DataFrame:
    """
    Load NetCDF variables from TSV file.

    Args:
        tsv_file: Path to ecosim_input-netcdf_variables.tsv

    Returns:
        DataFrame with NetCDF variable specifications

    >>> df = load_netcdf_vars(Path("test.tsv"))  # doctest: +SKIP
    >>> 'variable-name' in df.columns  # doctest: +SKIP
    True
    """
    df = pd.read_csv(tsv_file, sep='\t')
    print(f"✓ Loaded {len(df)} NetCDF variables from {tsv_file.name}")
    return df


def load_bervo_terms(tsv_file: Path) -> pd.DataFrame:
    """
    Load BERVO ontology terms from TSV file.

    Args:
        tsv_file: Path to bervo-terms.tsv

    Returns:
        DataFrame with BERVO term definitions

    >>> df = load_bervo_terms(Path("bervo.tsv"))  # doctest: +SKIP
    >>> 'EcoSIM Variable Name' in df.columns  # doctest: +SKIP
    True
    """
    df = pd.read_csv(tsv_file, sep='\t')
    print(f"✓ Loaded {len(df)} BERVO terms from {tsv_file.name}")
    return df


def align_variables(netcdf_df: pd.DataFrame, bervo_df: pd.DataFrame) -> pd.DataFrame:
    """
    Align NetCDF variables with BERVO terms.

    The alignment is performed by matching:
    1. NetCDF 'variable-name' with BERVO 'EcoSIM Variable Name'
    2. NetCDF 'variable-name' with BERVO 'EcoSIM Other Names' (if available)

    Args:
        netcdf_df: DataFrame with NetCDF variable specs
        bervo_df: DataFrame with BERVO terms

    Returns:
        DataFrame with aligned variables and BERVO annotations

    >>> netcdf = pd.DataFrame({'variable-name': ['RAINH', 'TMPH']})  # doctest: +SKIP
    >>> bervo = pd.DataFrame({'EcoSIM Variable Name': ['RAINH'], 'ID': ['BERVO:001']})  # doctest: +SKIP
    >>> result = align_variables(netcdf, bervo)  # doctest: +SKIP
    >>> len(result)  # doctest: +SKIP
    2
    """
    # Create primary mapping from BERVO by EcoSIM Variable Name
    bervo_by_var = bervo_df.set_index('EcoSIM Variable Name')

    # Create secondary mapping from EcoSIM Other Names if column exists
    bervo_by_other = {}
    if 'EcoSIM Other Names' in bervo_df.columns:
        for idx, row in bervo_df.iterrows():
            other_names = row.get('EcoSIM Other Names', '')
            if pd.notna(other_names) and other_names:
                # Split by pipe if multiple names
                names = [n.strip() for n in str(other_names).split('|') if n.strip()]
                for name in names:
                    if name not in bervo_by_other:
                        bervo_by_other[name] = row

    # Select key BERVO columns to add to the output
    bervo_cols = [
        'ID',
        'Label (description)',
        'Category',
        'Definition',
        'has_units',
        'Parents',
    ]

    # Filter to only include columns that exist
    available_cols = [col for col in bervo_cols if col in bervo_by_var.columns]

    # Add BERVO columns with prefix
    aligned_df = netcdf_df.copy()

    def get_bervo_value(var_name, col_name):
        """Get BERVO value, trying primary then secondary mapping."""
        # Try primary mapping (EcoSIM Variable Name)
        if var_name in bervo_by_var.index:
            return bervo_by_var.loc[var_name, col_name]
        # Try secondary mapping (EcoSIM Other Names)
        elif var_name in bervo_by_other:
            return bervo_by_other[var_name].get(col_name)
        return None

    for col in available_cols:
        aligned_df[f'BERVO_{col}'] = aligned_df['variable-name'].apply(
            lambda x: get_bervo_value(x, col)
        )

    # Calculate match statistics
    matched = aligned_df['BERVO_ID'].notna().sum()
    total = len(aligned_df)
    match_rate = (matched / total * 100) if total > 0 else 0

    print(f"\nAlignment Statistics:")
    print(f"  Total NetCDF variables: {total}")
    print(f"  Matched with BERVO: {matched}")
    print(f"  Unmatched: {total - matched}")
    print(f"  Match rate: {match_rate:.1f}%")
    print(f"  Alternative names checked: {len(bervo_by_other)}")

    return aligned_df


def write_aligned_output(df: pd.DataFrame, output_file: Path):
    """
    Write aligned variables to TSV file.

    Args:
        df: DataFrame with aligned variables
        output_file: Path to output TSV file
    """
    df.to_csv(output_file, sep='\t', index=False)
    print(f"\n✓ Wrote aligned variables to: {output_file}")


def generate_unmatched_report(df: pd.DataFrame, output_file: Path):
    """
    Generate a report of unmatched variables for curation.

    Args:
        df: DataFrame with aligned variables
        output_file: Path to unmatched report file
    """
    unmatched = df[df['BERVO_ID'].isna()].copy()

    if len(unmatched) == 0:
        print("✓ All variables matched!")
        return

    # Select relevant columns for curation
    report_cols = [
        'source_file',
        'type',
        'variable-name',
        'variable-long_name',
        'variable-unit',
    ]

    available_report_cols = [col for col in report_cols if col in unmatched.columns]
    unmatched_report = unmatched[available_report_cols]

    unmatched_report.to_csv(output_file, sep='\t', index=False)
    print(f"✓ Wrote unmatched variables report to: {output_file}")
    print(f"  → {len(unmatched)} variables need BERVO curation")


def main():
    """Main entry point."""
    # Default file paths
    netcdf_vars_file = Path(
        "hackathon-case_study-experimental_warming_nitrogen/derived/ecosim_input-netcdf_variables.tsv"
    )
    bervo_file = Path("bervo/bervo-terms.tsv")
    output_dir = Path("derived")

    # Override with command line arguments if provided
    if len(sys.argv) > 1:
        netcdf_vars_file = Path(sys.argv[1])
    if len(sys.argv) > 2:
        bervo_file = Path(sys.argv[2])
    if len(sys.argv) > 3:
        output_dir = Path(sys.argv[3])

    # Validate input files exist
    if not netcdf_vars_file.exists():
        print(f"✗ NetCDF variables file not found: {netcdf_vars_file}")
        sys.exit(1)

    if not bervo_file.exists():
        print(f"✗ BERVO terms file not found: {bervo_file}")
        sys.exit(1)

    # Create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    print("EcoSIM NetCDF Variables → BERVO Alignment")
    print("=" * 60)

    # Load data
    netcdf_df = load_netcdf_vars(netcdf_vars_file)
    bervo_df = load_bervo_terms(bervo_file)

    # Perform alignment
    print("\nAligning variables...")
    aligned_df = align_variables(netcdf_df, bervo_df)

    # Write outputs
    output_file = output_dir / "ecosim_input-netcdf_variables-bervo_aligned.tsv"
    write_aligned_output(aligned_df, output_file)

    unmatched_file = output_dir / "ecosim_input-netcdf_variables-unmatched.tsv"
    generate_unmatched_report(aligned_df, unmatched_file)

    print("\n✓ Alignment complete!")


if __name__ == "__main__":
    main()

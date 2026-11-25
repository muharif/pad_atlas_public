"""Check deployment file allowlist and obvious private columns; not a disclosure review."""
from pathlib import Path
import sys
import pyarrow.parquet as pq
EXPECTED = {'clinical_correlations.parquet', 'module_summary.parquet', 'mrna_mirna_integration.parquet', 'mirna_de.parquet', 'senescence_consensus.parquet', 'pathway_results.parquet', 'features.parquet', 'overview_table1.parquet', 'pathway_concordance.parquet', 'mirna_expression_summary.parquet', 'mrna_meta.parquet', 'module_membership.parquet', 'integration_pathways.parquet', 'senescence_features.parquet', 'cohort_composition.parquet', 'mrna_deseq2.parquet', 'mrna_expression_summary.parquet'}
root=Path(sys.argv[1])
actual={p.name for p in root.glob('*.parquet')}
if actual != EXPECTED:
    raise SystemExit(f'Missing: {EXPECTED-actual}; unexpected: {actual-EXPECTED}')
for p in sorted(root.glob('*.parquet')):
    cols=set(pq.ParquetFile(p).schema_arrow.names)
    forbidden={c for c in cols if c.lower() in {'sample_id','patient_id','subject_id','participant_id','tpm','log_tpm','log2_tpm1','base_mean','basemean'}}
    if forbidden: raise SystemExit(f'{p.name}: forbidden columns {forbidden}')
print('17 expected datasets present; obvious private columns absent. Manual release review still required.')

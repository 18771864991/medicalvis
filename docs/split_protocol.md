# Split Protocol

## Problem Addressed

NL2VIS datasets can accidentally leak evaluation information when paraphrases,
chart variants, or nearly identical visualization queries are split randomly.
In MedicalVis-35K, the full corpus is released as a 35,184-question resource,
but evaluation should use a split that prevents the same data query from
appearing in both training and held-out sets.

## Released Split

The release provides train, development, and test files under
`data/splits/sql_disjoint/`.

Procedure:

1. Build the full corpus from all MedicalVis-35K records.
2. Normalize `vis_query.data_part.sql_part` by lowercasing and collapsing
   whitespace.
3. Group all records with the same normalized SQL data query.
4. Assign whole groups to train/dev/test with a deterministic seed.
5. Validate that no normalized SQL data query appears in more than one split.

Audit result:

| pair | SQL signature overlap |
| --- | ---: |
| train/dev | 0 |
| train/test | 0 |
| dev/test | 0 |

## Reporting Recommendation

Use this wording in papers:

> We report results on the released MedicalVis-35K split, where
> all natural-language requests sharing the same normalized SQL data query are
> assigned to the same partition. This protocol prevents identical data-query
> signatures from crossing train/dev/test boundaries.

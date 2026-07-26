# MedicalVis-35K

MedicalVis-35K is a clinical natural-language-to-visualization dataset for
building and evaluating systems that translate medical questions into
executable visualization queries.

The dataset contains 35,184 natural-language questions paired with 16,592
visualization queries over a clinical relational schema. Each example includes
a natural-language request, a structured visualization query, SQL data logic,
and chart metadata. Executed query results are intentionally excluded from the
public release.

## Dataset At A Glance

| Field | Value |
| --- | ---: |
| Natural-language questions | 35,184 |
| Visualization queries | 16,592 |
| SQL signature groups | 9,995 |
| Chart types | Bar, Line, Scatter, Pie |
| Difficulty levels | Easy, Medium, Hard, Extra Hard |

Released split sizes:

| split | visualization queries | NL questions | SQL groups |
| --- | ---: | ---: | ---: |
| train | 13,274 | 28,152 | 7,998 |
| dev | 1,659 | 3,532 | 998 |
| test | 1,659 | 3,500 | 999 |

## Repository Layout

```text
data/
├── manifest.json
├── medicalvis_35k.jsonl.gz
├── medicalvis_35k_questions.csv
├── schema/
└── splits/
    └── sql_disjoint/
        ├── train.jsonl.gz
        ├── dev.jsonl.gz
        └── test.jsonl.gz

examples/
├── representative_examples.json
└── html/

docs/
├── split_protocol.md
└── kdd_dataset_statement.md

scripts/
├── build_public_release.py
└── validate_splits.py
```

## Loading

```python
import gzip
import json

with gzip.open("data/splits/sql_disjoint/train.jsonl.gz", "rt", encoding="utf-8") as f:
    train = [json.loads(line) for line in f]

print(train[0]["NLQs"][0])
print(train[0]["vis_query"]["data_part"]["sql_part"])
```

To validate the released split files:

```bash
python scripts/validate_splits.py
```

## Representative Examples

Representative query examples are available in:

```text
examples/representative_examples.json
examples/html/
```

They cover different chart types, difficulty levels, and clinical query
patterns, including prescription summaries, diagnosis-conditioned cohorts,
temporal aggregation, and multi-table joins. Eight representative HTML
renderings are included as limited public examples; they contain the aggregated
values required to display those eight charts. Executed values for the full
dataset are not redistributed.

## Data Use

This repository does not redistribute the raw clinical database. Users who need
to execute SQL against the source clinical tables must prepare the database in
an authorized local environment according to the upstream data-use
requirements. The public JSONL files omit `vis_obj.x_data` and
`vis_obj.y_data`; users must execute the released SQL locally to obtain the
values required for rendering. The only pre-rendered results are the eight
representative HTML examples under `examples/html/`.

## License

MedicalVis-35K uses separate licenses for dataset and software components:

- Original dataset annotations, metadata, split definitions, representative
  examples, and documentation are licensed under
  [CC BY 4.0](LICENSES/CC-BY-4.0.txt).
- Source code and scripts under `scripts/` are licensed under the
  [MIT License](LICENSES/MIT.txt).

The underlying MIMIC clinical database is not redistributed. It remains
subject to the applicable PhysioNet license, data use agreement, credentialing,
training, and citation requirements. See the top-level [LICENSE](LICENSE) file
for the complete scope and third-party-data notice.

## Citation

Citation metadata will be added with the paper release.

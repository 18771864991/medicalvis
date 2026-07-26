# Dataset Card: MedicalVis-35K

## Summary

MedicalVis-35K is a dataset for clinical NL2VIS research. It pairs natural
language visualization requests with structured visualization queries, SQL data
logic, and chart metadata. Executed query results and rendered charts are
intentionally excluded from the full JSONL release. Eight representative HTML
renderings are provided separately as limited public examples.

## Intended Tasks

- Natural language to visualization query generation
- Medical chart-type and visual-design planning
- SQL-grounded visualization generation
- Evaluation of clinical visualization agents

## Dataset Composition

| component | count |
| --- | ---: |
| Natural-language questions | 35,184 |
| Visualization queries | 16,592 |
| Train NL questions | 28,152 |
| Dev NL questions | 3,532 |
| Test NL questions | 3,500 |

Chart distribution:

| chart | count |
| --- | ---: |
| Scatter | 4,708 |
| Line | 4,671 |
| Bar | 4,018 |
| Pie | 3,195 |

Difficulty distribution:

| level | count |
| --- | ---: |
| Easy | 509 |
| Medium | 7,016 |
| Hard | 8,181 |
| Extra Hard | 886 |

## Evaluation Split

Use the files under `data/splits/`. The split groups records by normalized SQL
data query before assigning them to train/dev/test. This avoids cross-split
reuse of the same data request and makes test performance less dependent on
memorizing repeated query signatures.

## Data Fields

Each JSONL record contains:

| field | description |
| --- | --- |
| `id` | Stable public MedicalVis ID |
| `NLQs` | Natural-language paraphrases |
| `vis_query` | DVQ string, chart directive, SQL data part, and hardness |
| `vis_obj` | Chart type and visual-channel names; executed `x_data` and `y_data` are omitted |
| `metadata` | Chart type, hardness, source trace, and SQL signature hash |

## Limitations

MedicalVis-35K is designed for benchmark research. It should not be used for
clinical decision making. The public repository contains visualization-query
and schema artifacts, but not the raw clinical database, executed query
results, or rendered charts. Users must execute the released SQL in an
authorized local environment to obtain visualization values. The separately
identified HTML examples contain only the aggregated values needed to display
those eight representative charts.

## License

The original MedicalVis-35K dataset annotations, metadata, split definitions,
representative examples, and documentation are licensed under CC BY 4.0.
Software under `scripts/` is licensed under the MIT License. These licenses do
not apply to the underlying MIMIC clinical database or other third-party
clinical resources, which remain governed by their applicable PhysioNet
licenses and data use agreements. See [LICENSE](LICENSE) for details.

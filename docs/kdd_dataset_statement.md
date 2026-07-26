# Suggested KDD Dataset Statement

MedicalVis-35K contains 35,184 natural-language visualization requests paired
with 16,592 SQL-grounded visualization queries over a clinical relational
schema. The corpus covers four chart families, Bar, Line, Scatter, and Pie, and
four difficulty levels from single-table aggregations to multi-table
conditioned cohorts.

For evaluation, we release a canonical SQL-disjoint train/dev/test split. The
split groups examples by normalized SQL data query before partitioning, so
paraphrases and chart variants over the same data request remain in the same
partition. This design avoids train/test contamination from repeated data-query
signatures while preserving the full 35K natural-language corpus for training
and analysis.

Recommended short form:

> MedicalVis-35K is a 35,184-question clinical NL2VIS corpus with 16,592
> visualization queries. We evaluate on the public SQL-disjoint split, which
> prevents repeated SQL data-query signatures from crossing train/dev/test
> boundaries.

Avoid saying that `35K` is the number of unique visualization queries. It is
the number of natural-language questions. The unique visualization-query count
is 16,592.


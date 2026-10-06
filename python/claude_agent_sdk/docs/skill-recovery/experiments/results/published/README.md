# Published recovery evidence

These are complete structured projections of locally retained experiment captures. Operator identity, Enterprise session context identifiers and machine paths are sanitized. Raw captures, historical failure reports and consumed reservations remain unchanged locally. Harness configuration files are omitted without inspection.

[The publication manifest](manifest.json) maps each unchanged raw file SHA-256 to its exported SHA-256. Embedded run hashes and transcript bindings identify original raw evidence; they do not assert that sanitized bytes equal original recovery inputs. Original call IDs, tool inputs/results, model replies, usage, histories, failure dispositions and cleanup receipts remain preserved. The exported SQLite databases retain their schema and sanitized text fields.

The projections document the observed runs. They are not replacement runtime checkpoints and do not authorize replay, effect execution or model calls. Use an operator's own explicitly approved raw checkpoint for live continuation.

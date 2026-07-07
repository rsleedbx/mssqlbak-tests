# Risk Fixture Coverage

| Risk | Recent failure class | First hit | Second hit | Status |
|---|---|---|---|---|
| Alias type name map | AdventureWorks Flag/NameStyle alias BIT text | `alias_types_full` known aliases | `alias_types_full` unknown alias rows with `base_sql_type` | pass |
| XML serialization regex | AdventureWorks XML empty-element and CR serialization | `xmlcoverage_full` untyped XML | `typed_xml_full` typed empty/CR/entity/numeric rows | pass |
| WKT number regex | AdventureWorks geography WKT precision | `spatial_edge_full` basic shapes | `spatial_edge_full` high-precision/ZM/collection rows | pass |
| Float text precision | max finite float sidecar text overflow | `boundarycoverage_full`, `ncci_types_full` CCI paths | `float_extreme_full` rowstore path | pass |
| Cells sample digest mode | sampled/capped cells sidecar digest authority | `cci_bitpack_probe_bigint_full` sampled sidecar | synthetic capped digest-only sidecar | pass |
| `sql_variant` canonicalization | `sql_variant` per-value type text drift | `sql_variant_extract_full` int/decimal/text/datetime rows | `sql_variant_extract_full` guid/binary/datetimeoffset/scale rows | pass |

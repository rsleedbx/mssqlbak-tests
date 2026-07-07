# Sample-corpus coverage

Extractability of the real Microsoft `sql-server-samples` corpus (`tests/fixtures/samples/`, git-ignored). **Generated** by `python -m tools.sample_coverage`; see [SAMPLE_TESTING_PLAN.md](SAMPLE_TESTING_PLAN.md) for method and roadmap, and [ROBUSTNESS_COVERAGE.md](ROBUSTNESS_COVERAGE.md) for the skip contract on the committed fixtures.

**Surveyed 54 downloaded sample(s):** 1643 of 1692 user tables supported; 47 database(s) fully supported (every table extractable, 0 skips).

Each row reflects `classify_table` (metadata-only extractability), not value correctness — see [ENGINE_VALIDATION.md](ENGINE_VALIDATION.md).

| Sample | SS Version | MB | Container | Metadata | Tables | Supported | Skips | Time |
|--------|:----------:|---:|-----------|:--------:|-------:|----------:|-------|-----:|
| `TutorialDB.bak` | 2016 | 0 | compressed | ok | 1 | **1** | — | 0s |
| `Pubs.bak` | 2019 | 0 | compressed | ok | 11 | **11** | — | 0s |
| `AdventureWorksLT2025.bak` | 2025 | 2 | compressed | ok | 12 | **12** | — | 0s |
| `Chinook.bak` | ~2021 | 6 | MTF | ok | 11 | **11** | — | 0s |
| `IndexInternals2008.bak` | 2008/R2 | 6 | compressed | ok | 2 | **2** | — | 0s |
| `AdventureWorksLT2016.bak` | 2016 | 7 | MTF | ok | 12 | **12** | — | 0s |
| `AdventureWorksLT2017.bak` | 2017 | 7 | MTF | ok | 12 | **12** | — | 0s |
| `AdventureWorksLT2019.bak` | 2019 | 8 | MTF | ok | 12 | **12** | — | 0s |
| `AdventureWorksLT2022.bak` | 2022 | 8 | MTF | ok | 12 | **12** | — | 0s |
| `data.gov.bak` | 2019 | 12 | compressed | ok | 1 | **1** | — | 0s |
| `Chinook-id-pk.bak` | ~2021 | 12 | MTF | ok | 11 | **11** | — | 0s |
| `EmployeeCaseStudySampleDB2012.bak` | 2012 | 13 | compressed | ok | 2 | **2** | — | 0s |
| `AdventureWorksLT2014.bak` | 2014 | 13 | MTF | ok | 12 | **12** | — | 0s |
| `AdventureWorksLT2012.bak` | 2012 | 13 | MTF | ok | 12 | **12** | — | 0s |
| `WideWorldImportersDW-Full.bacpac` | — | 20 | BACPAC | ok | 29 | 11 | no-data ×18 | 0s |
| `WideWorldImportersDW-Standard.bacpac` | — | 21 | BACPAC | ok | 29 | 11 | no-data ×18 | 0s |
| `AdventureWorksDW2014.bak` | 2014 | 21 | compressed | ok | 31 | **31** | — | 1s |
| `AdventureWorksDW2016.bak` | 2016 | 21 | compressed | ok | 31 | **31** | — | 1s |
| `AdventureWorksDW2012.bak` | 2012 | 22 | compressed | ok | 31 | **31** | — | 1s |
| `AdventureWorksDW2017.bak` | 2017 | 22 | compressed | ok | 31 | **31** | — | 1s |
| `AdventureWorksDW2025.bak` | 2025 | 24 | compressed | ok | 31 | **31** | — | 1s |
| `SalesDB2014.bak` | 2014 | 28 | compressed | ok | 4 | **4** | — | 1s |
| `AdventureWorks2014.bak` | 2014 | 45 | compressed | ok | 71 | **71** | — | 1s |
| `AdventureWorks2012.bak` | 2012 | 45 | compressed | ok | 71 | **71** | — | 1s |
| `AdventureWorks2016.bak` | 2016 | 46 | compressed | ok | 71 | **71** | — | 1s |
| `WideWorldImportersDW-Full.bak` | 2016 | 48 | compressed | ok | 29 | **29** | — | 1s |
| `AdventureWorks2025.bak` | 2025 | 48 | compressed | ok | 71 | **71** | — | 1s |
| `AdventureWorks2017.bak` | 2017 | 48 | compressed | ok | 71 | **71** | — | 1s |
| `WideWorldImportersDW-Standard.bak` | 2016 | 51 | compressed | ok | 29 | **29** | — | 1s |
| `CreditBackup100.bak` | 2008/R2 | 53 | compressed | ok | 9 | **9** | — | 1s |
| `WideWorldImporters-Standard.bacpac` | — | 58 | BACPAC | ok | 48 | 46 | no-data ×2 | 0s |
| `WideWorldImporters-Full.bacpac` | — | 58 | BACPAC | ok | 48 | 46 | no-data ×2 | 0s |
| `WideWorldImporters-Standard_old.bacpac` | — | 58 | BACPAC | ok | 48 | 46 | no-data ×2 | 0s |
| `WideWorldImporters-Full_old.bacpac` | — | 59 | BACPAC | ok | 48 | 46 | no-data ×2 | 0s |
| `AdventureWorksDW2008R2.bak` | 2008/R2 | 74 | MTF | ok | 28 | **28** | — | 0s |
| `AdventureWorksDW2019.bak` | 2019 | 97 | MTF | ok | 31 | **31** | — | 0s |
| `AdventureWorksDW2022.bak` | 2022 | 97 | MTF | ok | 31 | **31** | — | 0s |
| `NYCTaxi_Sample.bak` | 2016 | 97 | MTF | ok | 2 | **2** | — | 0s |
| `BaseballData.bak` | ~2013 | 114 | MTF | ok | 25 | **25** | — | 0s |
| `WideWorldImporters-Standard_old.bak` | 2016 | 121 | compressed | ok | 48 | **48** | — | 3s |
| `WideWorldImporters-Standard.bak` | 2016 | 121 | compressed | ok | 48 | **48** | — | 3s |
| `WideWorldImporters-Full_old.bak` | 2016 | 121 | compressed | ok | 48 | **48** | — | 3s |
| `WideWorldImporters-Full.bak` | 2016 | 121 | compressed | ok | 48 | **48** | — | 3s |
| `AdventureWorks2016_EXT.bak` | 2016 | 125 | compressed | ok | 92 | **92** | — | 3s |
| `AdventureWorks2008R2.bak` | 2008/R2 | 181 | MTF | ok | 71 | **71** | — | 0s |
| `SalesDBOriginal.bak` | ~2006 | 192 | MTF | ok | 5 | 0 | no-columns ×5 | 0s |
| `AdventureWorks2019.bak` | 2019 | 199 | MTF | ok | 71 | **71** | — | 0s |
| `AdventureWorks2022.bak` | 2022 | 200 | MTF | ok | 71 | **71** | — | 0s |
| `tpcxbb_1gb.bak` | 2016 | 234 | compressed | ok | 30 | **30** | — | 3s |
| `GeneralHospital.bak` | ~2018 | 316 | MTF | ok | 13 | **13** | — | 0s |
| `dba.stackexchange.com.bak` | 2019 | 489 | compressed | ok | 8 | **8** | — | 12s |
| `ContosoRetailDW.bak` | 2008/R2 | 630 | compressed | ok | 26 | **26** | — | 11s |
| `StackOverflowMini.bak` | 2022 | 759 | compressed | ok | 9 | **9** | — | 18s |
| `AdventureWorksDW2016_EXT.bak` | 2016 | 883 | compressed | ok | 33 | **33** | — | 15s |

## Extraction performance

Measured by `--perf` (full row extraction into a temp Delta directory). **Bytes in** = uncompressed page bytes read (pages × 8 KiB); **bytes out** = in-memory Arrow batch bytes before Delta compression.

| Sample | Rows in | Rows out | In bytes | Out bytes | In rows/s | Out rows/s | In MB/s | Out MB/s | Time |
|--------|--------:|---------:|---------:|----------:|----------:|-----------:|--------:|---------:|-----:|
| `TutorialDB.bak` | 453 | 453 | 32.0 KB | 19.6 KB | 8,164 | 8,164 | 590.6 KB/s | 361.3 KB/s | 0s |
| `Pubs.bak` | 255 | 255 | 88.0 KB | 39.7 KB | 2,029 | 2,029 | 717.1 KB/s | 323.1 KB/s | 0s |
| `AdventureWorksLT2025.bak` | 4,277 | 4,277 | 1.5 MB | 1.2 MB | 29,595 | 29,595 | 10.6 MB/s | 8.6 MB/s | 0s |
| `Chinook.bak` | 16,075 | 16,075 | 904.0 KB | 510.6 KB | 205,957 | 205,957 | 11.9 MB/s | 6.7 MB/s | 0s |
| `IndexInternals2008.bak` | 159,840 | 159,840 | 62.4 MB | 53.9 MB | 246,657 | 246,657 | 101.0 MB/s | 87.3 MB/s | 1s |
| `AdventureWorksLT2016.bak` | 4,277 | 4,277 | 1.5 MB | 1.2 MB | 49,217 | 49,217 | 17.6 MB/s | 14.3 MB/s | 0s |
| `AdventureWorksLT2017.bak` | 4,277 | 4,277 | 1.5 MB | 1.2 MB | 51,902 | 51,902 | 18.6 MB/s | 15.1 MB/s | 0s |
| `AdventureWorksLT2019.bak` | 4,277 | 4,277 | 1.5 MB | 1.2 MB | 49,058 | 49,058 | 17.6 MB/s | 14.2 MB/s | 0s |
| `AdventureWorksLT2022.bak` | 4,277 | 4,277 | 1.5 MB | 1.2 MB | 47,380 | 47,380 | 17.0 MB/s | 13.8 MB/s | 0s |
| `data.gov.bak` | 150,482 | 150,482 | 42.3 MB | 42.5 MB | 184,151 | 184,151 | 54.2 MB/s | 54.5 MB/s | 1s |
| `Chinook-id-pk.bak` | 16,075 | 16,075 | 904.0 KB | 510.6 KB | 145,906 | 145,906 | 8.4 MB/s | 4.7 MB/s | 0s |
| `EmployeeCaseStudySampleDB2012.bak` | 159,840 | 159,840 | 62.4 MB | 57.1 MB | 165,903 | 165,903 | 68.0 MB/s | 62.1 MB/s | 1s |
| `AdventureWorksLT2014.bak` | 4,276 | 4,276 | 1.5 MB | 1.2 MB | 51,364 | 51,364 | 18.3 MB/s | 15.4 MB/s | 0s |
| `AdventureWorksLT2012.bak` | 4,276 | 4,276 | 1.5 MB | 1.2 MB | 53,862 | 53,862 | 19.2 MB/s | 16.1 MB/s | 0s |
| `WideWorldImportersDW-Full.bacpac` | 922,709 | 922,709 | 162.9 MB | 129.6 MB | 1,237,696 | 1,237,696 | 229.1 MB/s | 182.2 MB/s | 1s |
| `WideWorldImportersDW-Standard.bacpac` | 922,709 | 922,709 | 162.9 MB | 129.6 MB | 1,214,555 | 1,214,555 | 224.8 MB/s | 178.8 MB/s | 1s |
| `AdventureWorksDW2014.bak` | 1,060,805 | 1,060,805 | 73.0 MB | 70.2 MB | 744,631 | 744,631 | 53.7 MB/s | 51.7 MB/s | 1s |
| `AdventureWorksDW2016.bak` | 1,060,820 | 1,060,820 | 73.1 MB | 70.2 MB | 742,700 | 742,700 | 53.7 MB/s | 51.5 MB/s | 1s |
| `AdventureWorksDW2012.bak` | 1,060,804 | 1,060,804 | 73.0 MB | 70.2 MB | 734,811 | 734,811 | 53.0 MB/s | 51.0 MB/s | 1s |
| `AdventureWorksDW2017.bak` | 1,060,820 | 1,060,820 | 73.1 MB | 70.2 MB | 734,270 | 734,270 | 53.1 MB/s | 51.0 MB/s | 1s |
| `AdventureWorksDW2025.bak` | 1,047,563 | 1,047,563 | 69.5 MB | 67.8 MB | 727,671 | 727,671 | 50.6 MB/s | 49.4 MB/s | 1s |
| `SalesDB2014.bak` | 6,735,507 | 6,735,507 | 188.9 MB | 132.6 MB | 2,354,230 | 2,354,230 | 69.2 MB/s | 48.6 MB/s | 3s |
| `AdventureWorks2014.bak` | 760,811 | 760,811 | 88.2 MB | 71.1 MB | 213,265 | 213,265 | 25.9 MB/s | 20.9 MB/s | 4s |
| `AdventureWorks2012.bak` | 760,810 | 760,810 | 88.2 MB | 71.2 MB | 211,397 | 211,397 | 25.7 MB/s | 20.7 MB/s | 4s |
| `AdventureWorks2016.bak` | 760,838 | 760,838 | 88.2 MB | 71.2 MB | 209,386 | 209,386 | 25.5 MB/s | 20.5 MB/s | 4s |
| `WideWorldImportersDW-Full.bak` | 119,120 | 119,120 | 27.6 MB | 19.8 MB | 47,473 | 47,473 | 11.5 MB/s | 8.3 MB/s | 3s |
| `AdventureWorks2025.bak` | 760,167 | 760,167 | 85.4 MB | 70.2 MB | 211,159 | 211,159 | 24.9 MB/s | 20.4 MB/s | 4s |
| `AdventureWorks2017.bak` | 760,837 | 760,837 | 88.3 MB | 71.2 MB | 198,914 | 198,914 | 24.2 MB/s | 19.5 MB/s | 4s |
| `WideWorldImportersDW-Standard.bak` | 923,643 | 923,643 | 145.4 MB | 130.0 MB | 243,464 | 243,464 | 40.2 MB/s | 35.9 MB/s | 4s |
| `CreditBackup100.bak` | 15,554 | 15,554 | 664.0 KB | 649.4 KB | 14,284 | 14,284 | 624.4 KB/s | 610.6 KB/s | 1s |
| `WideWorldImporters-Standard.bacpac` | 4,713,833 | 4,713,833 | 407.2 MB | 356.8 MB | 2,773,743 | 2,773,743 | 251.3 MB/s | 220.2 MB/s | 2s |
| `WideWorldImporters-Full.bacpac` | 4,713,833 | 4,713,833 | 407.2 MB | 356.8 MB | 2,915,655 | 2,915,655 | 264.1 MB/s | 231.4 MB/s | 2s |
| `WideWorldImporters-Standard_old.bacpac` | 4,713,832 | 4,713,832 | 407.2 MB | 356.8 MB | 3,009,541 | 3,009,541 | 272.6 MB/s | 238.9 MB/s | 2s |
| `WideWorldImporters-Full_old.bacpac` | 4,713,832 | 4,713,832 | 407.2 MB | 356.8 MB | 2,852,594 | 2,852,594 | 258.4 MB/s | 226.4 MB/s | 2s |
| `AdventureWorksDW2008R2.bak` | 282,009 | 282,009 | 39.4 MB | 36.3 MB | 425,016 | 425,016 | 62.2 MB/s | 57.4 MB/s | 1s |
| `AdventureWorksDW2019.bak` | 1,060,820 | 1,060,820 | 73.1 MB | 70.2 MB | 1,041,095 | 1,041,095 | 75.2 MB/s | 72.2 MB/s | 1s |
| `AdventureWorksDW2022.bak` | 1,060,820 | 1,060,820 | 73.1 MB | 70.2 MB | 1,045,144 | 1,045,144 | 75.5 MB/s | 72.5 MB/s | 1s |
| `BaseballData.bak` | 493,104 | 493,104 | 49.2 MB | 47.2 MB | 559,564 | 559,564 | 58.6 MB/s | 56.1 MB/s | 1s |
| `WideWorldImporters-Standard_old.bak` | 4,713,832 | 4,713,832 | 444.8 MB | 330.4 MB | 635,145 | 635,145 | 62.8 MB/s | 46.7 MB/s | 7s |
| `WideWorldImporters-Standard.bak` | 4,713,833 | 4,713,833 | 444.8 MB | 330.4 MB | 641,033 | 641,033 | 63.4 MB/s | 47.1 MB/s | 7s |
| `WideWorldImporters-Full_old.bak` | 4,411,163 | 4,411,163 | 260.4 MB | 300.4 MB | 588,008 | 588,008 | 36.4 MB/s | 42.0 MB/s | 8s |
| `WideWorldImporters-Full.bak` | 4,411,164 | 4,411,164 | 260.4 MB | 300.4 MB | 574,205 | 574,205 | 35.5 MB/s | 41.0 MB/s | 8s |
| `AdventureWorks2016_EXT.bak` | 1,192,157 | 1,192,157 | 215.3 MB | 139.1 MB | 169,289 | 169,289 | 32.1 MB/s | 20.7 MB/s | 7s |
| `AdventureWorks2008R2.bak` | 760,811 | 760,811 | 87.9 MB | 71.1 MB | 286,152 | 286,152 | 34.7 MB/s | 28.1 MB/s | 3s |
| `AdventureWorks2019.bak` | 760,837 | 760,837 | 88.0 MB | 71.2 MB | 282,845 | 282,845 | 34.3 MB/s | 27.7 MB/s | 3s |
| `AdventureWorks2022.bak` | 760,837 | 760,837 | 88.0 MB | 71.2 MB | 281,495 | 281,495 | 34.1 MB/s | 27.6 MB/s | 3s |
| `tpcxbb_1gb.bak` | 94,044 | 94,044 | 3.0 MB | 2.2 MB | 28,252 | 28,252 | 952.4 KB/s | 694.9 KB/s | 3s |
| `GeneralHospital.bak` | 2,175,940 | 2,175,940 | 280.9 MB | 308.0 MB | 403,789 | 403,789 | 54.7 MB/s | 59.9 MB/s | 5s |
| `dba.stackexchange.com.bak` | 2,968,576 | 2,968,576 | 1.1 GB | 1.0 GB | 149,755 | 149,755 | 58.9 MB/s | 54.8 MB/s | 20s |
| `ContosoRetailDW.bak` | 34,326,475 | 34,326,475 | 1.2 GB | 4.4 GB | 642,008 | 642,008 | 24.0 MB/s | 88.7 MB/s | 53s |
| `StackOverflowMini.bak` | 8,097,337 | 8,097,337 | 1.6 GB | 1.6 GB | 236,926 | 236,926 | 49.0 MB/s | 48.8 MB/s | 34s |
| `AdventureWorksDW2016_EXT.bak` | 1,060,805 | 1,060,805 | 73.0 MB | 70.2 MB | 70,516 | 70,516 | 5.1 MB/s | 4.9 MB/s | 15s |

## Not downloaded

Fetch with `python -m tools.fetch_sample_baks`:

- `telcoedw2.bak`
- `velibDB.bak`

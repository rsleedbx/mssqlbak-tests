


mssqlbak did not have .bak file specs.  we reversed engeneered the specs based on emperical test.  based on the code to date, can we create a draft specs and figure out what are the areas we are guessing.  then create test .bak to create formalized specs? @docs/BAK_FORMAT_SPEC.md @docs/BAK_SPEC_FIXTURES.md is our current plan.  plan make them better.

is the following way to create additional .bak close the gap.

take all sqlserver dataypes. int, float, varchar, ...
make a list of all sqlserver datatypes that can be a primary key.  so if int and varchar are the only two that can be primer key
we want at least 4 tables where the primarky key for each data type to be at first, last, next to first, next to last.  2 x 4 = we have at least 8 tables
take all sqlserver datatypes and arrange them in a random order. float, int, varchar
num of columns in a table is random.  lets say we pick 6.  then float int, varchar, float, int, varchar
the first column that can be a primary key is is int, so the first int will be the primary key
we than randomize index, column store, null, not null, default value, compute columns, partitioning, idendity, any other features that can be accepted into the columns
the max column is 1024 in sqlserver, so we want tables with 1024, 1023 numnber of columns
the minimun column count is the number of datatypes in sqlserver.

Once the baseline spec is estimated, you must systematically push the boundaries to close gaps and confirm accuracy:Equivalence Partitioning & Boundary Analysis: Divide all possible inputs into groups that the system treats identically (valid and invalid). Tests are created to stress the exact boundaries between these partitions.Fuzz Testing / Property-Based Testing: Configure fuzzers to throw massive amounts of random, edge-case data at the estimated spec to uncover unexpected states or crashes. If an input violates an assumption, the spec is updated.Model-Based Testing (MBT) & Mutation Testing: Feed your estimated spec model into MBT tools to automatically generate hundreds of test cases. To ensure completeness, inject artificial faults ("mutations") into the system; if your test suite doesn't catch them, your spec is incomplete.Differential Testing: Run your estimated spec in parallel with the empirical data, and eventually the actual system. Any divergence between the two highlights a missing rule in your specification.
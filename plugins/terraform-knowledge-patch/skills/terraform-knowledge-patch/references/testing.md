# Testing

## Test Parallelism (1.12)

`terraform test` accepts `-parallelism=n` and individual `run` blocks can be annotated for parallel execution.

## Test Variable Definitions (1.13)

`variable` blocks can be declared directly in `.tftest.hcl` files.

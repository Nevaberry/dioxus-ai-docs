# State & Backends

## S3 Native State Locking (1.11)

`use_lockfile = true` in S3 backend replaces DynamoDB-based locking. DynamoDB locking args are deprecated.

```hcl
terraform {
  backend "s3" {
    bucket       = "my-state"
    key          = "terraform.tfstate"
    use_lockfile = true  # no DynamoDB needed
  }
}
```

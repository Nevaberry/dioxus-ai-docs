# Compute, Networking, and Edge

Use this reference for regions, VPC connectivity, IP addressing, NAT, flow logs, and network-facing service behavior.

## Contents

- [Regional and multi-region placement](#regional-and-multi-region-placement)
- [VPC ingress, egress, and addressing](#vpc-ingress-egress-and-addressing)
- [Network security and diagnostics](#network-security-and-diagnostics)

## Regional and multi-region placement

### Bangkok region availability (2026-01)

BigQuery, Cloud Run, GKE, and Pub/Sub are available in the Bangkok region, `asia-southeast3`.

### Regional availability (2025-03)

BigQuery, Cloud Run, and Pub/Sub are available in `europe-north2`; Cloud Run also adds `northamerica-south1`, and Cloud Run GPUs add `europe-west1`.


## VPC ingress, egress, and addressing

### Direct VPC egress address consumption (2025-03)

Cloud Run services using Direct VPC egress now consume twice as many IP addresses as running instances for each instance's lifetime plus up to 20 minutes, reduced from four times as many.

### Direct VPC egress for Cloud Run jobs (2025-04)

Direct VPC egress support for Cloud Run jobs is GA.

### Direct VPC ingress for Cloud Run worker pools (2026-02)

A Cloud Run worker pool can use Direct VPC ingress so every worker instance receives a private address on the selected network and subnet. Workers can retrieve their private IP addresses from the metadata server for internal VPC communication.

### External IPv6 from Cloud Run (2025-11)

GA dual-stack subnets let Cloud Run resources use Direct VPC egress for IPv4 and internal IPv6 traffic while sending external IPv6 traffic to the public internet.

### Internal IPv6 from Cloud Run (2025-01)

In Preview, Cloud Run services and jobs can use dual-stack subnets with Direct VPC egress to send both IPv4 and internal IPv6 traffic into a VPC network.

### Private NAT for Direct VPC egress (2025-05)

In Preview, Cloud Run Direct VPC egress can use Private NAT.


## Network security and diagnostics

### BigQuery Omni VPC allowlists (2025-01)

GA BigQuery Omni VPC allowlists can restrict access to AWS S3 buckets and Azure Blob Storage to specific BigQuery Omni VPCs.

### VPC Flow Logs for Cloud Run (2025-10)

In Preview, VPC Flow Logs can observe Cloud Run traffic that uses Direct VPC egress.

# Terraform ☁️

## Overview
This project provides the complete Terraform infrastructure for **pdfrag** on Google Cloud Platform (GCP).  
The architecture emphasizes:
- reproducible and stable deployments
- security best practices (least privilege, locked-down SSH)
- manual control of sensitive resources

## Code & Naming Conventions
Use **hyphen naming** for all variables:
- Correct: `vm-name`
- Avoid: `vm_name`
This aligns with GCP resource naming conventions and avoids conflicts.

## Prerequisites for manual Terraform deployments
### Install the Google Provider
https://registry.terraform.io/providers/hashicorp/google/latest

### Basic Terraform Commands
```
terraform init
terraform apply
terraform destroy
```

### Service Account Credentials
Store the service account key as:
```
credentials.json
```
⚠ Never commit this file.

# Service Accounts
## Terraform Service Account (Infrastructure)
Required roles:
- Compute Instance Admin (v1)
- Compute Network Admin
- Compute Security Admin
- Viewer
- Storage Object Admin
- Monitoring Editor
- Artifact Registry Administrator
- Service Account User

Also add to Billing (Billing Account Administrator) but for this you need to go to Billing / Account management and add the service account to the billing account manually.
(Also dont forget to change the billing account in the variables.tf file)

## CI/CD Service Account (Build & Push)
Required roles:
- Artifact Registry Writer
- Storage Object Admin

# APIs to enable manually
Do not enable APIs via Terraform to avoid over-permissioning.

Enable these in GCP:
- Cloud Resource Manager API
- Compute Engine API
- Artifact Registry API
- Billing Budget API

# GCP Resources - create manually

## VPC & Firewall
With custom firewall rules:

Allowed:
- 80 (HTTP)
- 443 (HTTPS)

Blocked:
- 22 (SSH) — access via GCP browser SSH only.

# Manual Tasks before deployment

### Terraform State Bucket
Remote state stored in:
```
rag-tf-state-bucket
```

### Static IP
Create manually and reference in `variables.tf`.

Reason:
- prevent IP rotation
- keep DNS stable between deployments

### Artifact Registry
Create manually:
```
pdfrag
```

Policies:
- cleanup old artifacts
- keep the 2 newest builds

### Persistent Disk for SSL
Disk name:
```
docker-ssl-data-disk
```

Used to store SSL certificates permanently.

## Security Considerations
- Least privilege everywhere
- No public SSH port
- No API auto-enablement via Terraform

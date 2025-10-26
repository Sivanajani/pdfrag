terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "7.6.0"
    }
  }

  required_version = ">= 1.13.3"
}
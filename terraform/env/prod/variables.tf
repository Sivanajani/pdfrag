variable "docker-tag" {
  type = string
  default = "latest"
  description = "give the docker image tag to be used it can be sha, git-version or latest"
}

variable "nginx-proxy-tag" {
  type = string
  default = "2678-alpine"
  description = "give the docker image tag to be used"
}

variable "acme-companion-tag" {
  type = string
  default = "2.6.1"
  description = "give the docker image tag to be used"
}

variable "project-id" {
  type = string
  default = "pdfrag-prod"
}

variable "region" {
  type = string
  default = "europe-west6"
}

variable "zone" {
  type = string
  default = "europe-west6-b"
}

variable "time-zone" {
  type = string
  default = "Europe/Zurich"
}

variable "network" {
  type = string
  default = "default"
}

variable "vm-name" {
  type = string
  default = "pdfrag"
}

variable "project-name" {
  type = string
  default = "pdfrag"
}

variable "start-cron" {
  type = string
  default = "0 6 * * 1-5"
}

variable "stop-cron" {
  type = string
  default = "00 20 * * 1-5"
}

variable "static-ip-address" {
  type = string
  default = "34.158.21.231"
  description = "need to be created manually in the same region as the VM"
}

variable  "vm-service-account-email"  {
  type = string
  default = "terraform@pdfrag-prod.iam.gserviceaccount.com"
}

variable "notify-email" {
  type = string
  default = "sivanajani@swissntech.ch"
}

variable "billing-account" {
  type = string
  default = "013895-B47378-55CA41"
  description = "must be in the format XXXXXX-XXXXXX-XXXXXX and filled manually"
}
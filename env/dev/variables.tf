variable "project-id" {
  type = string
  default = "project-trial-420614"
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
  default = "rag"
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
  default = "34.65.97.194"
  description = "need to be created manually in the same region as the VM"
}

variable "notify-email" {
  type = string
  default = "sivanajani@gmail.com"
}

variable "billing-account" {
  type = string
  default = "014E4F-539B22-915166"
  description = "must be in the format XXXXXX-XXXXXX-XXXXXX and filled manually" //TODO must be given from outside
}
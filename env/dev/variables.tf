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

variable "static-ip-name" {
  type = string
  default = "rag-vm-static-ip"
}

variable "vm-name" {
  type = string
  default = "rag"
}

variable "start-cron" {
  type = string
  default = "0 6 * * *"
}

variable "stop-cron" {
  type = string
  default = "00 20 * * *"
}
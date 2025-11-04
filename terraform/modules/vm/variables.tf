variable "network" {
  type = string
}

variable "static-nat-ip" {
  type = string
}

variable "target-tags" {
  type = list(string)
  description = "Network tags to apply firewall rules to (must match VM tags)"
}

variable "vm-name" {
  type = string
}

variable "machine-type" {
  type = string
  default = "e2-medium"
}

variable "os-image" {
  type = string
  default = "ubuntu-os-cloud/ubuntu-2204-lts"
}

variable "disk-size-gb" {
  type = number
  default = 10
}

variable "disk-type" {
  type = string
  default = "pd-standard"
}
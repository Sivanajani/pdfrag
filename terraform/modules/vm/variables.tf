variable "docker-tag" {
  type = string
}

variable "nginx-proxy-tag" {
  type = string
}

variable "acme-companion-tag" {
  type = string
}

variable "network" {
  type = string
}

variable "static-nat-ip" {
  type = string
}

variable "project-name" {
  type = string
}

variable "project-id" {
  type = string
}

variable "target-tags" {
  type = list(string)
  description = "Network tags to apply firewall rules to (must match VM tags)"
}

variable "vm-name" {
  type = string
}

variable "zone" {
  type = string
}

variable  "vm-service-account-email"  {
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

variable "docker-ssl-disk_name" {
  type        = string
  description = "Name of the manually created persistent disk for Docker/nginx ssl data"
  default     = "docker-ssl-data-disk"
}

variable "virtual_host" {
  type = string
  default = "shaperag.com,www.shaperag.com"
  description = "The virtual host(s) for the frontend"
}

variable "letsencrypt_email" {
  type = string
  default = "sivanajani@swissntech.ch"
  description = "Email for Let's Encrypt notifications"
}
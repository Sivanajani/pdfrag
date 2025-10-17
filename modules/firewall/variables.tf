variable "network" {
  type = string
  description = "VPC name or self_link (e.g., 'default')"
}

variable "target_tags" {
  type = list(string)
  description = "Network tags to apply firewall rules to (must match VM tags)"
}

variable "name_prefix" {
  type = string
  description = "Prefix for firewall rule names"
}
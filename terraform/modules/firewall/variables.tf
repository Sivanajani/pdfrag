variable "network" {
  type = string
}

variable "target-tags" {
  type = list(string)
}

variable "name-prefix" {
  type = string
}

variable "allowed-protocol" {
  type = string
  default = "tcp"
}

variable "allowed-ports" {
  type = list(string)
  default = ["80", "443", "8000", "5173"]
}

variable "firewall-direction" {
  type = string
  default = "INGRESS"
}

variable "firewall-source-range" {
  type = list(string)
  default =  ["0.0.0.0/0"]
}
variable "project-id" {
  type = string
}

variable "notify-email" {
  type = string
}

variable "billing-account" {
  type = string
  description = "must be in the format XXXXXX-XXXXXX-XXXXXX and filled manually"
}

variable "currency-code" {
  type = string
  default = "CHF"
}

variable "budget-amount" {
  type = number
  default = 100
}

variable "thresholds" {
  type = list(number)
  default = [0.7, 0.9, 1.0]
}

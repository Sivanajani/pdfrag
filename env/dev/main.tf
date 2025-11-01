locals {
  # Network tags to apply firewall rules to (must match VM tags)
  target-tags = ["${var.vm-name}-web"]
  policy-name = "${var.vm-name}-off-hours"
}

module "firewall" {
  source = "../../modules/firewall"

  network = var.network
  target-tags = local.target-tags
  name-prefix = var.vm-name
}

module "vm" {
  source = "../../modules/vm"

  vm-name = var.vm-name
  static-nat-ip = var.static-ip-address
  network = var.network
  target-tags = local.target-tags
}

module "policy" {
  source = "../../modules/policy"

  name = local.policy-name
  region = var.region
  time-zone = var.time-zone
  start-cron = var.start-cron
  stop-cron = var.stop-cron
}

module "billing" {
  source = "../../modules/billing"

  project-id = var.project-id
  billing-account = var.billing-account
  notify-email = var.notify-email
}

resource "google_compute_resource_policy_attachment" "off_hours_attach" {
  name     = module.policy.name
  project  = var.project-id
  zone     = var.zone
  instance = module.vm.name
}
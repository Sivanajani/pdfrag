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
  static-nat-ip = google_compute_address.static_ip.address
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

resource "google_compute_address" "static_ip" {
  name   = var.static-ip-name
  region = var.region

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_compute_resource_policy_attachment" "off_hours_attach" {
  name     = module.policy.name
  project  = var.project-id
  zone     = var.zone
  instance = module.vm.name
}
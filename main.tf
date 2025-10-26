locals {
  # Network tags to apply firewall rules to (must match VM tags)
  target_tags = ["${var.vm_name}-web"]
}

provider "google" {
  project = var.project_id
  region = var.region
  zone = var.zone
  credentials = "./credentials.json"
}

module "firewall" {
  source = "./modules/firewall"

  network = var.network
  target_tags = local.target_tags
  name_prefix = var.vm_name
}

module "vm" {
  source = "./modules/vm"

  static_nat_ip = google_compute_address.static_ip.address
  network = var.network
  region = var.region
  project_id = var.project_id
  zone = var.zone
  target_tags = local.target_tags
}

module "policy" {
  source = "./modules/policy"
  name = "${var.vm_name}-off-hours"
  region = var.region
  time_zone = "Europe/Zurich"
  start_cron = "0 6 * * *"
  stop_cron = "00 20 * * *"
}

resource "google_compute_address" "static_ip" {
  name   = var.static_ip_name
  region = var.region
}

resource "google_compute_resource_policy_attachment" "off_hours_attach" {
  name     = module.policy.name
  project  = var.project_id
  zone     = var.zone
  instance = module.vm.name
}
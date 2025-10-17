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

resource "google_compute_address" "static_ip" {
  name   = var.static_ip_name
  region = var.region
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
  target_tags = local.target_tags
}
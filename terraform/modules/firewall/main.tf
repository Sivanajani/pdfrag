resource "google_compute_firewall" "web" {
  name = "${var.name-prefix}-allow-web"
  network = var.network

  allow {
    protocol = var.allowed-protocol
    ports = var.allowed-ports
  }

  direction = var.firewall-direction
  source_ranges = var.firewall-source-range
  target_tags = var.target-tags
}
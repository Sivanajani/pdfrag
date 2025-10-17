resource "google_compute_firewall" "web" {
  name = "${var.name_prefix}-allow-web"
  network = var.network

  allow {
    protocol = "tcp"
    ports = ["80", "443"]
  }

  direction = "INGRESS"
  source_ranges = ["0.0.0.0/0"]
  target_tags = var.target_tags
}
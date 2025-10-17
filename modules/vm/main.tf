resource "google_compute_instance" "vm" {
  name = var.vm_name
  machine_type = var.machine_type
  tags = var.target_tags

  boot_disk {
    initialize_params {
      image = var.os_image
      size = var.disk_size_gb
      type = var.disk_type
    }
  }

  network_interface {
    network = "default"

    access_config {
      nat_ip = var.static_nat_ip
    }
  }
}
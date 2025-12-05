resource "google_compute_instance" "vm" {
  name = var.vm-name
  machine_type = var.machine-type
  tags = var.target-tags

  boot_disk {
    initialize_params {
      image = var.os-image
    }
  }

  attached_disk {
    source = data.google_compute_disk.docker_ss_data.id
    device_name = var.docker-ssl-disk_name
    mode = "READ_WRITE"
  }

  network_interface {
    network = var.network

    access_config {
      nat_ip = var.static-nat-ip
    }
  }

  service_account {
    email  = var.vm-service-account-email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  metadata = {
    enable-oslogin = "TRUE"
    user-data = templatefile("${path.module}/templates/cloud-init.yaml.tftpl", {
      app_dir = "/opt/app"
      project_name = var.project-name
      project_id = var.project-id
      image_tag = var.docker-tag
      nginx_proxy_tag = var.nginx-proxy-tag
      acme_companion_tag = var.acme-companion-tag
      cert_device_name = var.docker-ssl-disk_name
    })
  }
}

data "google_compute_disk" "docker_ss_data" {
  name = var.docker-ssl-disk_name
  zone = var.zone
}
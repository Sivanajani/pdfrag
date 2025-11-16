resource "google_compute_instance" "vm" {
  name = var.vm-name
  machine_type = var.machine-type
  tags = var.target-tags

  boot_disk {
    initialize_params {
      image = var.os-image
      size = var.disk-size-gb
      type = var.disk-type
    }
  }

  network_interface {
    network = var.network

    access_config {
      nat_ip = var.static-nat-ip
    }
  }

  service_account {
    email  = "terraform@project-trial-420614.iam.gserviceaccount.com"
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
    })
  }
}
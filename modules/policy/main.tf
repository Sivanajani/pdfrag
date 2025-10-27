resource "google_compute_resource_policy" "off-hours" {
  name   = var.name
  region = var.region

  instance_schedule_policy {
    time_zone = var.time-zone

    vm_start_schedule {
      schedule = var.start-cron
    }

    vm_stop_schedule {
      schedule = var.stop-cron
    }
  }
}
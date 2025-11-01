resource "google_monitoring_notification_channel" "billing_email" {
  display_name = "Billing Budget Alerts"
  type         = "email"
  labels = {
    email_address = var.notify-email
  }
}

resource "google_billing_budget" "monthly" {
  billing_account = var.billing-account
  display_name = "Monthly Budget (${var.currency-code} ${var.budget-amount})"

  amount {
    specified_amount {
      currency_code = var.currency-code
      units = var.budget-amount
    }
  }

  budget_filter {
    projects = ["projects/${var.project-id}"]
  }

  dynamic "threshold_rules" {
    for_each = var.thresholds
    content {
      threshold_percent = threshold_rules.value
    }
  }

  all_updates_rule {
    disable_default_iam_recipients = false
    monitoring_notification_channels = [
      google_monitoring_notification_channel.billing_email.name
    ]
  }
}
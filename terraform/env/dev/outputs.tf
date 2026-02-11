output "public_ip" {
  description = "Open https://<this-ip> in your browser"
  value = module.vm.public_ip
}
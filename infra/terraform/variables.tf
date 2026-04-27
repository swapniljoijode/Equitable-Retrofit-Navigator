variable "project_name" {
  type    = string
  default = "equitable-retrofit-navigator"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "container_image" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "ecs_security_group_id" {
  type = string
}

variable "alb_security_group_id" {
  type = string
}

variable "desired_count" {
  type    = number
  default = 1
}

variable "max_capacity" {
  type    = number
  default = 4
}

variable "min_capacity" {
  type    = number
  default = 1
}

variable "cpu" {
  type    = number
  default = 512
}

variable "memory" {
  type    = number
  default = 1024
}

variable "certificate_arn" {
  type        = string
  description = "ACM certificate ARN for HTTPS listener."
}

variable "api_auth_key" {
  type      = string
  sensitive = true
}

variable "openai_api_key" {
  type      = string
  sensitive = true
}

variable "google_api_key" {
  type      = string
  sensitive = true
}

variable "nyc_open_data_app_token" {
  type      = string
  sensitive = true
  default   = ""
}

variable "enable_waf" {
  type    = bool
  default = true
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.this.name
}

output "ecs_service_name" {
  value = aws_ecs_service.app.name
}

output "alb_dns_name" {
  value = aws_lb.api.dns_name
}

output "lambda_function_name" {
  value = aws_lambda_function.app_runner.function_name
}

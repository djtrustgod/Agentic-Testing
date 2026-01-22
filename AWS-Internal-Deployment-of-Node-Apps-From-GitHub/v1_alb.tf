# Internal ALB
resource "aws_lb" "internal" {
  name               = "nodejs-internal-alb"
  internal           = true  # Critical: Internal only
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb. id]
  subnets            = aws_subnet.private[*].id

  tags = { Name = "nodejs-internal-alb" }
}

# Target Group
resource "aws_lb_target_group" "app" {
  name        = "nodejs-app-tg"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }
}

# HTTPS Listener
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.internal. arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn  # ACM certificate

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app. arn
  }
}
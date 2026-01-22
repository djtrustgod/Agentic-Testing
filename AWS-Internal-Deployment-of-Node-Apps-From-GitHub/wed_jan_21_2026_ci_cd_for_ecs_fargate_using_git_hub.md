# Copilot Chat Conversation Export: CI/CD for ECS Fargate using GitHub

**User:** @djtrustgod
**Thread URL:** https://github.com/copilot/c/f71efb62-d7a4-4b0d-bfe4-95b3d19e8704

## @djtrustgod

What's the best way to publish Node.js based apps to AWS so they can only be accessed from inside the corporate network.

## Copilot

This is a great question about deploying Node.js applications securely on AWS with restricted network access. Here are the best approaches:

## Best Practices for Private Node.js Deployment on AWS

### 1. **Amazon VPC (Virtual Private Cloud) with Private Subnets**
The foundation of any internal-only deployment: 
- Deploy your Node.js app in **private subnets** (no internet gateway)
- Use **VPC endpoints** for AWS services (S3, DynamoDB, etc.)
- Connect your corporate network via **AWS Direct Connect** or **Site-to-Site VPN**

### 2. **Deployment Options**

#### **Option A: EC2 in Private Subnets**
```
Corporate Network → VPN/Direct Connect → VPC → Private Subnet → EC2 (Node.js)
```
- Use an **internal Application Load Balancer (ALB)** for traffic distribution
- Configure **Security Groups** to only allow traffic from corporate IP ranges

#### **Option B: AWS Elastic Beanstalk (Private)**
- Deploy to a VPC-enabled Elastic Beanstalk environment
- Configure internal load balancer only
- Simple deployment with `eb deploy`

#### **Option C: Amazon ECS/EKS with Fargate (Private)**
- Containerize your Node.js app
- Deploy to private subnets with **awsvpc** network mode
- Use **AWS PrivateLink** for service access

#### **Option D: AWS Lambda with VPC**
- Deploy Lambda in your VPC's private subnets
- Access via **API Gateway (Private)** with VPC endpoint policies

### 3. **Network Security Configuration**

```hcl
# Example Security Group (Terraform)
resource "aws_security_group" "nodejs_app" {
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # Corporate network range only
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]  # Or restrict further
  }
}
```

### 4. **Corporate Network Connectivity**

| Method | Best For | Latency |
|--------|----------|---------|
| **AWS Direct Connect** | High bandwidth, consistent performance | Lowest |
| **Site-to-Site VPN** | Cost-effective, quick setup | Low-Medium |
| **Client VPN** | Individual user access | Medium |

### 5. **Additional Security Layers**
- **AWS WAF** on internal ALB for application-layer protection
- **AWS PrivateLink** to expose services without traversing the internet
- **VPC Flow Logs** for network monitoring
- **IAM roles** for secure AWS service access (no hardcoded credentials)

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Corporate Network                        │
└─────────────────────────┬───────────────────────────────────┘
                          │ VPN / Direct Connect
┌─────────────────────────▼───────────────────────────────────┐
│                        AWS VPC                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   Private Subnet                        │ │
│  │  ┌──────────────┐    ┌──────────────────────────────┐  │ │
│  │  │ Internal ALB │───▶│  Node.js App (ECS/EC2/EB)    │  │ │
│  │  └──────────────┘    └──────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start Recommendation

For most cases, I'd recommend **ECS Fargate in private subnets** with an **internal ALB**: 
1. Easy container deployment with `docker push` + task definition update
2. No server management
3. Auto-scaling built-in
4. Strong network isolation

Would you like more details on any of these approaches, or help with a specific deployment configuration? 

## @djtrustgod

Provide more details on the ECS Fargate option you recommended. 

## Copilot

## Deploying Node.js on Amazon ECS Fargate (Private Network)

Here's a comprehensive guide to deploying your Node.js app on ECS Fargate with internal-only access:

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Corporate Network                                 │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ AWS Direct Connect / Site-to-Site VPN
┌────────────────────────────────▼────────────────────────────────────────┐
│                              AWS VPC                                     │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                      Private Subnet (AZ-a)                          │ │
│  │   ┌─────────────┐      ┌─────────────────────────────────┐         │ │
│  │   │ Internal    │      │  ECS Fargate Task (Node.js)     │         │ │
│  │   │ ALB         │─────▶│  - Container:  node-app          │         │ │
│  │   │             │      │  - CPU: 256, Memory: 512        │         │ │
│  │   └─────────────┘      └─────────────────────────────────┘         │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                      Private Subnet (AZ-b)                          │ │
│  │                        ┌─────────────────────────────────┐         │ │
│  │            ───────────▶│  ECS Fargate Task (Node.js)     │         │ │
│  │                        │  - Container: node-app          │         │ │
│  │                        │  - CPU: 256, Memory:  512        │         │ │
│  │                        └─────────────────────────────────┘         │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  VPC Endpoints:  ECR, CloudWatch Logs, Secrets Manager, S3        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Implementation

### 1. Prepare Your Node.js Application

**Dockerfile:**
```dockerfile name=Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy package files first for better caching
COPY package*. json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Run as non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001
USER nodejs

EXPOSE 3000

CMD ["node", "server.js"]
```

**Health check endpoint (important for ALB):**
```javascript name=server.js
const express = require('express');
const app = express();

// Health check endpoint for ALB
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.get('/', (req, res) => {
  res.json({ message: 'Hello from ECS Fargate!' });
});

const PORT = process.env. PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

---

### 2. Infrastructure Setup (Terraform)

**VPC and Networking:**
```hcl name=vpc.tf
# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = { Name = "nodejs-app-vpc" }
}

# Private Subnets (no internet gateway attached)
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc. main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = { Name = "private-subnet-${count.index + 1}" }
}

# Security Group for ALB (internal)
resource "aws_security_group" "alb" {
  name        = "internal-alb-sg"
  description = "Security group for internal ALB"
  vpc_id      = aws_vpc.main. id

  ingress {
    description = "HTTPS from corporate network"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # Corporate network CIDR
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  name        = "ecs-tasks-sg"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Traffic from ALB only"
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

**VPC Endpoints (required for private subnet access to AWS services):**
```hcl name=vpc-endpoints.tf
# ECR API Endpoint
resource "aws_vpc_endpoint" "ecr_api" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.region}.ecr.api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true
}

# ECR Docker Endpoint
resource "aws_vpc_endpoint" "ecr_dkr" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true
}

# S3 Gateway Endpoint (for ECR image layers)
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private. id]
}

# CloudWatch Logs Endpoint
resource "aws_vpc_endpoint" "logs" {
  vpc_id              = aws_vpc. main.id
  service_name        = "com.amazonaws.${var.region}.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true
}

# Secrets Manager Endpoint (if using secrets)
resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true
}

resource "aws_security_group" "vpc_endpoints" {
  name        = "vpc-endpoints-sg"
  vpc_id      = aws_vpc. main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc. main.cidr_block]
  }
}
```

**ECS Cluster and Service:**
```hcl name=ecs. tf
# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "nodejs-app-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Task Execution Role (for pulling images, logging)
resource "aws_iam_role" "ecs_task_execution" {
  name = "ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts: AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks. amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution. name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Task Definition
resource "aws_ecs_task_definition" "nodejs" {
  family                   = "nodejs-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution. arn

  container_definitions = jsonencode([{
    name  = "nodejs-app"
    image = "${aws_ecr_repository.app.repository_url}:latest"
    
    portMappings = [{
      containerPort = 3000
      protocol      = "tcp"
    }]

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:3000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.app.name
        "awslogs-region"        = var.region
        "awslogs-stream-prefix" = "ecs"
      }
    }

    environment = [
      { name = "NODE_ENV", value = "production" },
      { name = "PORT", value = "3000" }
    ]
  }])
}

# ECS Service
resource "aws_ecs_service" "nodejs" {
  name            = "nodejs-app-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.nodejs.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*]. id
    security_groups  = [aws_security_group. ecs_tasks.id]
    assign_public_ip = false  # Critical:  No public IP
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "nodejs-app"
    container_port   = 3000
  }

  depends_on = [aws_lb_listener.https]
}
```

**Internal Application Load Balancer:**
```hcl name=alb.tf
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
```

---

### 3. Deployment Pipeline

**Push image to ECR and update service:**
```bash name=deploy.sh
#!/bin/bash
set -e

AWS_REGION="us-east-1"
AWS_ACCOUNT_ID="123456789012"
ECR_REPO="nodejs-app"
IMAGE_TAG="${GITHUB_SHA:-latest}"

# Authenticate with ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push image
docker build -t $ECR_REPO:$IMAGE_TAG . 
docker tag $ECR_REPO:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws. com/$ECR_REPO: $IMAGE_TAG

# Update ECS service (forces new deployment)
aws ecs update-service \
  --cluster nodejs-app-cluster \
  --service nodejs-app-service \
  --force-new-deployment \
  --region $AWS_REGION

echo "Deployment initiated.  Monitor at: https://console.aws.amazon.com/ecs"
```

---

### 4. Auto Scaling Configuration

```hcl name=autoscaling.tf
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.nodejs.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Scale based on CPU utilization
resource "aws_appautoscaling_policy" "cpu" {
  name               = "cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
```

---

## Key Security Highlights

| Feature | Implementation |
|---------|----------------|
| **No Public IP** | `assign_public_ip = false` in ECS service |
| **Internal ALB** | `internal = true` on load balancer |
| **Security Groups** | ALB only accepts traffic from corporate CIDR |
| **VPC Endpoints** | AWS services accessed privately, no internet required |
| **TLS Encryption** | HTTPS listener with modern TLS policy |
| **Least Privilege** | Minimal IAM roles for task execution |

---

## Accessing the Application

Once deployed, users on your corporate network can access the app via the internal ALB DNS:
```
https://nodejs-internal-alb-1234567890.us-east-1.elb.amazonaws. com
```

You can create a friendly DNS name using **Route 53 Private Hosted Zone**:
```hcl
resource "aws_route53_record" "app" {
  zone_id = aws_route53_zone.private.zone_id
  name    = "myapp.internal.company.com"
  type    = "A"

  alias {
    name                   = aws_lb.internal.dns_name
    zone_id                = aws_lb.internal.zone_id
    evaluate_target_health = true
  }
}
```

---

Would you like me to elaborate on any specific part, such as CI/CD integration with GitHub Actions, secrets management, or monitoring setup? 

## @djtrustgod

Provide more details on the CI/CD of the Fargate installation using GitHub Actions.

## Copilot

## CI/CD Pipeline for ECS Fargate with GitHub Actions

Here's a comprehensive GitHub Actions workflow for deploying your Node.js app to ECS Fargate: 

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          GitHub Repository                               │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Push to main branch                                                │ │
│  └──────────────────────────────┬─────────────────────────────────────┘ │
└─────────────────────────────────┼───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        GitHub Actions Workflow                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐  │
│  │   Test &    │─▶│   Build     │─▶│   Push to   │─▶│   Deploy to   │  │
│  │   Lint      │  │   Image     │  │   ECR       │  │   ECS         │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                                              │
                                  ┌───────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              AWS                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐  │
│  │  Amazon ECR     │───▶│  ECS Fargate    │◀───│  Internal ALB       │  │
│  │  (Container     │    │  (Running       │    │  (Corporate         │  │
���  │   Registry)     │    │   Tasks)        │    │   Access Only)      │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: AWS Authentication Setup

### Option A: OpenID Connect (OIDC) - Recommended

OIDC is the most secure method—no long-lived credentials stored in GitHub.

**Create IAM OIDC Provider and Role (Terraform):**
```hcl name=github-oidc.tf
# GitHub OIDC Provider
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

# IAM Role for GitHub Actions
resource "aws_iam_role" "github_actions" {
  name = "github-actions-ecs-deploy"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = aws_iam_openid_connect_provider.github.arn
      }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          # Replace with your GitHub org/repo
          "token.actions. githubusercontent.com:sub" = "repo:your-org/your-repo: *"
        }
      }
    }]
  })
}

# Policy for ECR and ECS access
resource "aws_iam_role_policy" "github_actions" {
  name = "github-actions-ecs-policy"
  role = aws_iam_role.github_actions. id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr: UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = "arn:aws:ecr: ${var.region}:${var. account_id}:repository/nodejs-app"
      },
      {
        Effect = "Allow"
        Action = [
          "ecs: DescribeServices",
          "ecs: DescribeTaskDefinition",
          "ecs: DescribeTasks",
          "ecs:ListTasks",
          "ecs:RegisterTaskDefinition",
          "ecs:UpdateService"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          "arn:aws:iam::${var.account_id}:role/ecs-task-execution-role",
          "arn:aws:iam::${var.account_id}:role/ecs-task-role"
        ]
      }
    ]
  })
}

output "github_actions_role_arn" {
  value = aws_iam_role. github_actions.arn
}
```

---

## Step 2: GitHub Actions Workflow

### Complete CI/CD Workflow

```yaml name=.github/workflows/deploy. yml
name: Deploy to ECS Fargate

on:
  push:
    branches: [main]
  pull_request: 
    branches: [main]

env:
  AWS_REGION:  us-east-1
  ECR_REPOSITORY: nodejs-app
  ECS_CLUSTER: nodejs-app-cluster
  ECS_SERVICE:  nodejs-app-service
  CONTAINER_NAME: nodejs-app

permissions:
  id-token: write   # Required for OIDC
  contents: read
  pull-requests: write

jobs: 
  # ============================================
  # Job 1: Test and Lint
  # ============================================
  test: 
    name: Test & Lint
    runs-on:  ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint --if-present

      - name: Run tests
        run: npm test --if-present

      - name: Run security audit
        run: npm audit --audit-level=high
        continue-on-error: true

  # ============================================
  # Job 2: Build and Push to ECR
  # ============================================
  build:
    name:  Build & Push Image
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    outputs:
      image: ${{ steps.build-image.outputs.image }}

    steps:
      - name:  Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with: 
          role-to-assume:  arn:aws:iam:: ${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-ecs-deploy
          aws-region: ${{ env. AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Extract metadata for Docker
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ steps.login-ecr.outputs. registry }}/${{ env.ECR_REPOSITORY }}
          tags: |
            type=sha,prefix=
            type=raw,value=latest

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push Docker image
        id: build-image
        uses:  docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps. meta.outputs.tags }}
          labels: ${{ steps.meta. outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: false

      - name: Output image URI
        id: output-image
        run: |
          echo "image=${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}" >> $GITHUB_OUTPUT

  # ============================================
  # Job 3: Deploy to ECS
  # ============================================
  deploy:
    name: Deploy to ECS
    runs-on: ubuntu-latest
    needs: build
    environment: production
    
    steps: 
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets. AWS_ACCOUNT_ID }}: role/github-actions-ecs-deploy
          aws-region:  ${{ env.AWS_REGION }}

      - name: Download current task definition
        run: |
          aws ecs describe-task-definition \
            --task-definition nodejs-app \
            --query taskDefinition > task-definition.json

      - name: Update task definition with new image
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-definition.json
          container-name: ${{ env.CONTAINER_NAME }}
          image: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.${{ env.AWS_REGION }}.amazonaws.com/${{ env. ECR_REPOSITORY }}:${{ github.sha }}

      - name: Deploy to Amazon ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps. task-def.outputs.task-definition }}
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true

      - name:  Deployment summary
        run: |
          echo "## 🚀 Deployment Successful!" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Cluster:** ${{ env.ECS_CLUSTER }}" >> $GITHUB_STEP_SUMMARY
          echo "**Service:** ${{ env.ECS_SERVICE }}" >> $GITHUB_STEP_SUMMARY
          echo "**Image:** ${{ env.ECR_REPOSITORY }}: ${{ github.sha }}" >> $GITHUB_STEP_SUMMARY
```

---

## Step 3: Multi-Environment Deployment

For staging and production environments: 

```yaml name=.github/workflows/deploy-multi-env.yml
name: Multi-Environment Deploy

on:
  push: 
    branches: 
      - main        # Deploy to staging
      - release/*   # Deploy to production
  workflow_dispatch: 
    inputs:
      environment: 
        description: 'Environment to deploy to'
        required: true
        type: choice
        options: 
          - staging
          - production

permissions:
  id-token: write
  contents: read

jobs: 
  set-environment:
    runs-on: ubuntu-latest
    outputs:
      environment: ${{ steps.set-env.outputs.environment }}
    steps:
      - name: Determine environment
        id: set-env
        run: |
          if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
            echo "environment=${{ inputs.environment }}" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == refs/heads/release/* ]]; then
            echo "environment=production" >> $GITHUB_OUTPUT
          else
            echo "environment=staging" >> $GITHUB_OUTPUT
          fi

  deploy: 
    needs: set-environment
    runs-on: ubuntu-latest
    environment: ${{ needs.set-environment.outputs.environment }}
    
    env:
      ENVIRONMENT: ${{ needs.set-environment.outputs. environment }}

    steps:
      - name:  Checkout
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}

      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ steps.login-ecr.outputs. registry }}/${{ vars.ECR_REPOSITORY }}: ${{ github.sha }}
            ${{ steps.login-ecr.outputs.registry }}/${{ vars.ECR_REPOSITORY }}: ${{ env.ENVIRONMENT }}-latest

      - name: Download task definition
        run: |
          aws ecs describe-task-definition \
            --task-definition ${{ vars.TASK_DEFINITION_FAMILY }} \
            --query taskDefinition > task-definition.json

      - name:  Render task definition
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-definition.json
          container-name: ${{ vars. CONTAINER_NAME }}
          image: ${{ steps.login-ecr.outputs.registry }}/${{ vars.ECR_REPOSITORY }}:${{ github.sha }}

      - name: Deploy to ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          service: ${{ vars.ECS_SERVICE }}
          cluster: ${{ vars.ECS_CLUSTER }}
          wait-for-service-stability: true
```

---

## Step 4: GitHub Repository Configuration

### Required Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret Name | Description |
|-------------|-------------|
| `AWS_ACCOUNT_ID` | Your AWS account ID (e.g., `123456789012`) |

### Environment Variables (per environment)

Create environments (**Settings → Environments**) for `staging` and `production`:

| Variable Name | Staging Value | Production Value |
|---------------|---------------|------------------|
| `AWS_REGION` | `us-east-1` | `us-east-1` |
| `AWS_ROLE_ARN` | `arn:aws:iam::.. .:role/github-actions-staging` | `arn:aws:iam::...:role/github-actions-prod` |
| `ECS_CLUSTER` | `nodejs-staging-cluster` | `nodejs-prod-cluster` |
| `ECS_SERVICE` | `nodejs-staging-service` | `nodejs-prod-service` |
| `ECR_REPOSITORY` | `nodejs-app-staging` | `nodejs-app-prod` |
| `CONTAINER_NAME` | `nodejs-app` | `nodejs-app` |
| `TASK_DEFINITION_FAMILY` | `nodejs-app-staging` | `nodejs-app-prod` |

### Environment Protection Rules (Production)

For production, enable: 
- ✅ **Required reviewers** - Require approval before deployment
- ✅ **Wait timer** - Add delay before deployment starts
- ✅ **Deployment branches** - Restrict to `release/*` branches

---

## Step 5: Rollback Workflow

```yaml name=.github/workflows/rollback.yml
name: Rollback Deployment

on: 
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to rollback'
        required: true
        type: choice
        options:
          - staging
          - production
      image_tag:
        description: 'Image tag to rollback to (commit SHA)'
        required: true
        type: string

permissions: 
  id-token: write
  contents: read

jobs:
  rollback:
    runs-on: ubuntu-latest
    environment:  ${{ inputs.environment }}
    
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}
          aws-region:  ${{ vars.AWS_REGION }}

      - name: Verify image exists
        run: |
          aws ecr describe-images \
            --repository-name ${{ vars.ECR_REPOSITORY }} \
            --image-ids imageTag=${{ inputs. image_tag }}

      - name: Download current task definition
        run: |
          aws ecs describe-task-definition \
            --task-definition ${{ vars.TASK_DEFINITION_FAMILY }} \
            --query taskDefinition > task-definition.json

      - name: Update task definition with rollback image
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with: 
          task-definition: task-definition.json
          container-name: ${{ vars.CONTAINER_NAME }}
          image: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.${{ vars.AWS_REGION }}.amazonaws.com/${{ vars. ECR_REPOSITORY }}:${{ inputs.image_tag }}

      - name: Deploy rollback
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with: 
          task-definition: ${{ steps.task-def.outputs. task-definition }}
          service:  ${{ vars.ECS_SERVICE }}
          cluster: ${{ vars.ECS_CLUSTER }}
          wait-for-service-stability: true

      - name: Rollback summary
        run: |
          echo "## ⏪ Rollback Complete!" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Environment:** ${{ inputs.environment }}" >> $GITHUB_STEP_SUMMARY
          echo "**Rolled back to:** ${{ inputs.image_tag }}" >> $GITHUB_STEP_SUMMARY
```

---

## Step 6: PR Preview Workflow (Optional)

Add deployment previews for pull requests:

```yaml name=.github/workflows/pr-preview. yml
name: PR Preview

on:
  pull_request: 
    types: [opened, synchronize, reopened]

permissions:
  id-token: write
  contents:  read
  pull-requests: write

jobs:
  preview:
    runs-on: ubuntu-latest
    environment: preview
    
    steps:
      - name: Checkout
        uses:  actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}
          aws-region: ${{ vars. AWS_REGION }}

      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push preview image
        uses: docker/build-push-action@v5
        with:
          context: . 
          push: true
          tags: ${{ steps.login-ecr. outputs.registry }}/nodejs-app-preview:pr-${{ github.event.number }}

      - name: Deploy preview environment
        run: |
          # Create or update preview task definition and service
          # This is simplified - in practice you'd have a separate preview cluster
          echo "Preview deployed for PR #${{ github.event. number }}"

      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context. issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 🔍 Preview Deployment Ready! 
              
              **Preview URL:** \`https://pr-${{ github.event.number }}.preview.internal.company.com\`
              
              _This preview will be automatically cleaned up when the PR is closed._`
            })
```

---

## Summary:  Complete File Structure

```
your-repo/
├── .github/
│   └── workflows/
│       ├── deploy. yml           # Main CI/CD pipeline
│       ├── deploy-multi-env.yml # Multi-environment deployment
│       ├── rollback.yml         # Manual rollback workflow
│       └── pr-preview.yml       # PR preview deployments
├── terraform/
│   ├── github-oidc.tf          # IAM OIDC provider and role
│   ├── ecr. tf                  # ECR repository
│   ├── ecs. tf                  # ECS cluster, service, task definition
│   ├── vpc.tf                  # VPC and networking
│   ├── vpc-endpoints.tf        # VPC endpoints for private access
│   └── alb.tf                  # Internal Application Load Balancer
├── Dockerfile
├── package.json
└── server.js
```

---

## Key Security Features

| Feature | Implementation |
|---------|----------------|
| **No Long-Lived Credentials** | OIDC authentication with AWS |
| **Least Privilege IAM** | Scoped permissions for ECR/ECS only |
| **Environment Protection** | Required approvals for production |
| **Image Scanning** | ECR scan-on-push enabled |
| **Audit Trail** | All deployments logged in GitHub Actions |

Would you like me to provide more details on any specific aspect, such as adding Slack notifications, implementing blue-green deployments, or setting up monitoring with CloudWatch? 

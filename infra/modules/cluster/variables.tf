variable "name" {
    description = "Name prefix for resources"
    type = string
}

variable "owner" {
    description = "The owner of the resources created"
    type = string
}

variable "cluster_version" {
    description = "Kubernetes version for the EKS control plane"
    type = string
    default = "1.31"
}

variable "private_subnet_ids" {
    description = "Private subnet IDs where the control plane ENIs and nodes live"
    type = list(string)
}

variable "node_instance_type" {
    description = "EC2 instance type for the worker nodes"
    type = string
    default = "t3.medium"
}

variable "node_desired_size" {
    description = "Desired number of worker nodes"
    type = number
    default = 2
}

variable "node_min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 3
}
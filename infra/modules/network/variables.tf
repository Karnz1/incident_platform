variable "name" {
    description = "name prefix for resources"
    type        = string
}

variable "cidr_block" {
    description = "CIDR block for the VPC"
    type     = string
    default     = "10.10.0.0/16"
}

variable "owner" {
    description = "the owner of the resource created"
    type        = string
    default     = "Michael"
}


#subnets

variable "public_subnets" {
    description = "Map of AZ to CIDR block for public subnets"
    type        = map(string)
}

variable "private_subnets" {
    description = "Map of AZ to CIDR block for private subnets"
    type        = map(string)
}


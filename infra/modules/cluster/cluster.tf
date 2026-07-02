resource "aws_eks_cluster" "this" {
    name = var.name
    version = var.cluster_version
    role_arn = aws_iam_role.cluster.arn

    vpc_config {
        subnet_ids = var.private_subnet_ids
        endpoint_public_access = true
        endpoint_private_access = true
    }

    depends_on = [
        aws_iam_role_policy_attachment.cluster_policy
    ]
    
    tags = {
        Name  = var.name
        Owner = var.owner
  }
  #public_access_cidrs = ["your.ip/32"]
}
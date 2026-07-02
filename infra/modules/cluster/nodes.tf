resource "aws_eks_node_group" "this" {
    cluster_name = aws_eks_cluster.this.name
    node_group_name = "${var.name}-nodes"
    node_role_arn = aws_iam_role.node.arn
    subnet_ids = var.private_subnet_ids

    instance_types = [var.node_instance_type]

    scaling_config {
        desired_size = var.node_desired_size
        min_size = var.node_min_size
        max_size = var.node_max_size
    }

    update_config {
        max_unavailable = 1
    }

    depends_on = [
        aws_iam_role_policy_attachment.node_worker,
        aws_iam_role_policy_attachment.node_cni,
        aws_iam_role_policy_attachment.node_ecr,
    ]

    tags = {
        Name  = "${var.name}-nodes"
        Owner = var.owner
    }
}
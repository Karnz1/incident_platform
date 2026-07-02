# Fetch the cluster's TLS certificate to get its thumbprint
data "tls_certificate" "cluster" {
  url = aws_eks_cluster.this.identity[0].oidc[0].issuer
}

# Register the cluster's OIDC issuer with AWS IAM
resource "aws_iam_openid_connect_provider" "this" {
  url             = aws_eks_cluster.this.identity[0].oidc[0].issuer
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.cluster.certificates[0].sha1_fingerprint]

  tags = {
    Name  = "${var.name}-oidc"
    Owner = var.owner
  }
}
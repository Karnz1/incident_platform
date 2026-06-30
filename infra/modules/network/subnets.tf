resource "aws_subnet" "public" {
    for_each = var.public_subnets

    vpc_id                  = aws_vpc.this.id
    cidr_block              = each.value
    availability_zone       = each.key
    map_public_ip_on_launch = true

    tags = {
        Name                     = "${var.name}=public-${each.key}"
        Owner                    = var.owner
        "kubernetes.io/role/elb" = "1"
    }
}

resource "aws_subnet" "private" {
  for_each = var.private_subnets

  vpc_id            = aws_vpc.this.id
  cidr_block        = each.value
  availability_zone = each.key

  tags = {
    Name                              = "${var.name}-private-${each.key}"
    Owner                             = var.owner
    "kubernetes.io/role/internal-elb" = "1"
  }
}
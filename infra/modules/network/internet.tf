resource "aws_internet_gateway" "this" {
    vpc_id = aws_vpc.this.id

    tags = {
        Name  = "${var.name}-igw"
        Owner = var.owner
    }
}

resource "aws_eip" "nat" {
    domain = "vpc"

    tags = {
        Name  = "${var.name}-nat-eip"
        Owner = var.owner
    }
}

resource "aws_nat_gateway" "this" {
    allocation_id = aws_eip.nat.id
    subnet_id     = values(aws_subnet.public)[0].id

    tags = {
        Name  = "${var.name}-nat"
        Owner = var.owner
    }

    depends_on = [aws_internet_gateway.this]
}

resource "aws_route_table" "public" {
    vpc_id = aws_vpc.this.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.this.id
    }

    tags = {
        Name  = "${var.name}-public-rt"
        Owner = var.owner
    }
}

resource "aws_route_table_association" "public" {
    for_each = aws_subnet.public

    subnet_id      = each.value.id
    route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
    vpc_id = aws_vpc.this.id

    route {
        cidr_block     = "0.0.0.0/0"
        nat_gateway_id = aws_nat_gateway.this.id
    }

    tags = {
        Name  = "${var.name}-private-rt"
        Owner = var.owner
    }
}

resource "aws_route_table_association" "private" {
    for_each = aws_subnet.private

    subnet_id      = each.value.id
    route_table_id = aws_route_table.private.id
}
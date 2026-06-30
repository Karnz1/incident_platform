module "network" {
    source = "../module/network"

    name  = "incident-platform"
    owner = "Michael"

    public_subnets = {
        "eu-central-1a" = "10.10.1.0/24"
        "eu-central-1b" = "10.10.2.0/24"
    }

    private_subnets = {
        "eu-central-1a" = "10.10.11.0/24"
        "eu-central-1b" = "10.10.12.0/24"
    }
}
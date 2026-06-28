terraform {
    backend "s3" {
        bucket       = "inci-plat-tfstate"
        key          = "cluster/terraform.tfstate"
        region       = "eu-central-1"
        encrypt      = true
        use_lockfile = true
    }
}
    terraform {
      required_providers {
        google = {
          source  = "hashicorp/google"
          version = "~> 6.0"
        }
      }
    }

    provider "google" {
      project = "mlops-on-gcp-s25537"
      region  = "us-central1"
    }

resource "google_pubsub_topic" "deployment-topic" {
  name = "model-deployment-topic2"
}

import sys
import argparse
import json
from google.cloud import aiplatform

def main(args):


    aiplatform.init(project=args.project_id, location=args.region)

    # Wczytaj parametry z pliku JSON 
    with open(args.parameter_file, 'r') as f:
        # Zakładamy, że plik ma strukturę {"parameter_values": {...}}
        pipeline_parameters = json.load(f).get("parameter_values", {})

    print(f"Submitting pipeline job with parameters: {pipeline_parameters}")

    # Utwórz zadanie potoku
    job = aiplatform.PipelineJob(
        display_name=args.display_name,
        template_path=args.pipeline_spec_uri,
        parameter_values=pipeline_parameters,
        enable_caching=True, 
    )

    # Prześlij zadanie, używając podanego konta serwisowego
    job.submit(service_account=args.service_account)
    
    print(f"Pipeline job '{job.display_name}' submitted. View it at: {job.resource_name}")
    print("Waiting for pipeline to complete...")
    job.wait()
    print("Pipeline finished.")
    if job.state == aiplatform.gapic.PipelineState.PIPELINE_STATE_SUCCEEDED:
        print("Pipeline run succeeded.")
    else:
        print(f"Pipeline run failed. Final state: {job.state}")
        if job.error:
            print(f"Error details: {job.error}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger a Vertex AI Pipeline")
    parser.add_argument("--project-id", type=str, required=True, help="Google Cloud Project ID")
    parser.add_argument("--region", type=str, required=True, help="Google Cloud Region")
    parser.add_argument("--pipeline-spec-uri", type=str, required=True, help="GCS URI of the compiled pipeline JSON")
    parser.add_argument("--display-name", type=str, required=True, help="Display name for the pipeline run")
    parser.add_argument("--parameter-file", type=str, required=True, help="Path to the JSON file with runtime parameters")
    parser.add_argument("--service-account", type=str, required=True, help="Service account to run the pipeline job")
    
    args = parser.parse_args()
    main(args)
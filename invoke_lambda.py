import boto3
import json

session = boto3.Session()
lambda_client = session.client('lambda')

event = {
    "names": ["Alice", "Bob", "Charlie"]
}

response = lambda_client.invoke(
    FunctionName='HelloStudentFunction',
    InvocationType='RequestResponse',
    Payload=json.dumps(event)
)

response_payload = response['Payload'].read()
print(json.loads(response_payload))

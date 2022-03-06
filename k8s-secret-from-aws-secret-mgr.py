import boto3
import base64
import json
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os
import requests
import sys

base_url = "http://127.0.0.1:8001"

def event_loop():

    #config.load_kube_config()
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    url = '{}/apis/kubernetes-client.io/v1/secretmanagers?watch=true"'.format(base_url)
    r = requests.get(url, stream=True)

    for line in r.iter_lines():
        obj = json.loads(line)
        k8s_secret_name = obj["object"]["metadata"]["name"]
        namespace = obj["object"]["spec"]["namespace"]
        try:
            secret = v1.read_namespaced_secret(k8s_secret_name, namespace)
            print("K8s secret already exists!")
        except:
            print('K8s secret '+k8s_secret_name+' does not exist, therefore creating it...')
            secretType = obj["object"]["spec"]["secretType"]
            aws_secret_name = obj["object"]["spec"]["awsSecret"]
            region = obj["object"]["spec"]["region"]
            secrets_client = boto3.client('secretsmanager')
            secret_arn = 'arn:aws:secretsmanager:'+region+':'+os.environ.get("AWS_ACCOUNT")+':secret:'+aws_secret_name
            aws_secret = secrets_client.get_secret_value(SecretId=secret_arn).get('SecretString')

            if secretType == "docker":
                encodedBytes = base64.b64encode(aws_secret.encode("utf-8"))
                encodedStr = str(encodedBytes, "utf-8")
                secretType = "kubernetes.io/dockerconfigjson"
                data = {".dockerconfigjson": encodedStr}
            elif secretType == "opaque":
                secretType = "Opaque"
                aws_secret_dict = json.loads(aws_secret)
                for k, v in aws_secret_dict.items():
                    encodedBytes = base64.b64encode(v.encode("utf-8"))
                    aws_secret_dict[k] = str(encodedBytes, "utf-8")
                data = aws_secret_dict
          
            secret = client.V1Secret(   
                api_version="v1",
                data=data,
                kind="Secret",
                metadata=dict(name=k8s_secret_name, namespace=namespace),
                type=secretType,
            )

            v1.create_namespaced_secret(namespace, body=secret)

event_loop()
Deploying Python Application to AWS EC2 using GitHub Actions

This project demonstrates how to automate the deployment of a Python application to an AWS EC2 instance using GitHub Actions. The GitHub Actions workflow is set up to securely establish an SSH connection, install the necessary software on the EC2 instance, transfer the application code, and start the application.

Prerequisites
AWS Setup
EC2 Instance: Ensure you have a running EC2 instance with a public IP that can be accessed via SSH.
IAM User: The IAM user must have sufficient permissions, such as EC2FullAccess and S3FullAccess if using S3.
SSH Key Pair: Generate an SSH key pair in AWS for secure access to the EC2 instance. Store the private key as a GitHub secret.
GitHub Setup

Store the following secrets in your GitHub repository:
AWS_ACCESS_KEY_ID: Access key ID for your IAM user.
AWS_SECRET_ACCESS_KEY: Secret key for your IAM user.
EC2_SSH_KEY: Private SSH key for the EC2 instance.
EC2_HOST: The public IP address of your EC2 instance.
EC2_USER: The SSH username for the EC2 instance

Checkout Code
Fetches the latest version of your code from the repository.
Install Required Software on EC2
Establishes an SSH connection to the EC2 instance and installs any necessary software, such as Docker or Python, to run the application.
Transfer Application Code
The application code is uploaded to the EC2 instance via scp or optionally using S3 and the awscli.
Run the Application
Once the code is uploaded, the application is started. Depending on the setup, this can be done via Docker or by running the application directly on the server.
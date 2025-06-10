# Kubernetes MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server for Kubernetes operations. This server provides tools and resources for interacting with Kubernetes clusters across different cloud providers (AWS EKS, Azure AKS, Google GKE, and ROSA).

## Overview

The Kubernetes MCP Server allows AI assistants like Anthropic's Claude to interact with your Kubernetes clusters using the active context from your kubeconfig file. It provides a comprehensive set of tools and resources for managing Kubernetes resources, including:

- Listing and switching between Kubernetes contexts
- Managing namespaces, pods, deployments, services, configmaps, and secrets
- Viewing pod logs
- Executing commands in pods
- Creating, updating, and deleting resources using YAML
- Getting information about the cluster

## Features

### Tools

The Kubernetes MCP server provides the following tools:

| Tool Name | Description | Common Use Cases |
|-----------|-------------|------------------|
| `get_cluster_info` | Get information about the current Kubernetes cluster | Understanding cluster version, provider, and size |
| `get_contexts` | Get available Kubernetes contexts from kubeconfig | Switching between different clusters |
| `set_context` | Set the Kubernetes context to use | Changing the active cluster |
| `get_namespaces` | Get all namespaces in the cluster | Listing available namespaces |
| `get_pods` | Get all pods in the specified namespace | Monitoring pod status and health |
| `get_pod_logs` | Get logs from a pod | Troubleshooting application issues |
| `get_deployments` | Get all deployments in the specified namespace | Checking deployment status |
| `get_services` | Get all services in the specified namespace | Reviewing service endpoints |
| `get_configmaps` | Get all configmaps in the specified namespace | Inspecting configuration data |
| `get_secrets` | Get all secrets in the specified namespace | Managing sensitive information |
| `get_nodes` | Get all nodes in the cluster | Monitoring cluster capacity |
| `create_from_yaml` | Create Kubernetes resources from YAML content | Deploying new applications |
| `update_from_yaml` | Update Kubernetes resources from YAML content | Modifying existing resources |
| `delete_resource` | Delete a Kubernetes resource | Removing unwanted resources |
| `get_resource_yaml` | Get YAML representation of a Kubernetes resource | Exporting resource definitions |
| `exec_command` | Execute a command in a pod | Running diagnostics or maintenance tasks |

### Resources

The Kubernetes MCP server provides the following resources:

| Resource | Description | URI Template |
|----------|-------------|--------------|
| Cluster Info | Information about the current Kubernetes cluster | `k8s://{context}/info` |
| Namespaces | List of namespaces in the cluster | `k8s://{context}/namespaces` |
| Pods | List of pods in a namespace | `k8s://{context}/namespace/{namespace}/pods` |
| Deployments | List of deployments in a namespace | `k8s://{context}/namespace/{namespace}/deployments` |
| Services | List of services in a namespace | `k8s://{context}/namespace/{namespace}/services` |
| ConfigMaps | List of configmaps in a namespace | `k8s://{context}/namespace/{namespace}/configmaps` |
| Secrets | List of secrets in a namespace | `k8s://{context}/namespace/{namespace}/secrets` |
| Nodes | List of nodes in the cluster | `k8s://{context}/nodes` |
| Pod Logs | Logs from a pod | `k8s://{context}/namespace/{namespace}/pod/{pod}/logs` |
| Resource YAML | YAML representation of a resource | `k8s://{context}/namespace/{namespace}/resource/{kind}/{name}` |

## Installation

### Prerequisites

- Python 3.8 or higher
- Kubernetes Python client (`kubernetes` package)
- PyYAML and jsonschema packages
- A valid kubeconfig file with access to your Kubernetes clusters

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/kubernetes-mcp-server.git
cd kubernetes-mcp-server
```

#### 2. Create a Virtual Environment (Optional but Recommended)

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Install the Package

```bash
pip install -e .
```

This will install the package in development mode, along with all required dependencies.

#### 4. Configure the MCP Server for Your AI Assistant

##### For Anthropic's Claude (via Cline VSCode Extension)

Edit the file at:

**macOS/Linux:**
```
~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

**Windows:**
```
%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

Add the following configuration:

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "python",
      "args": ["-m", "kubernetes_mcp_server.server"],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

##### For Other AI Assistants

The Kubernetes MCP server follows the Model Context Protocol specification, so it can be integrated with any AI assistant that supports MCP. Refer to your AI assistant's documentation for specific integration instructions.

## Usage

Once the MCP server is installed and configured, your AI assistant will have access to the Kubernetes tools and resources provided by the server. You can use these tools to interact with your Kubernetes clusters.

### Example Commands

Here are some examples of how to use the Kubernetes MCP server with your AI assistant:

#### Basic Cluster Information

```
Can you get information about my current Kubernetes cluster?
```

#### Listing Resources

```
List all pods in the default namespace.
```

```
Show me all deployments across all namespaces.
```

#### Viewing Logs

```
Show me the logs from the pod named "my-pod" in the "my-namespace" namespace.
```

#### Creating Resources

```
Create a new deployment using this YAML:

apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

#### Deleting Resources

```
Delete the deployment named "nginx-deployment" in the default namespace.
```

#### Troubleshooting

```
List all deployments with less than desired replicas.
```

```
Check node resources to see if there are capacity issues.
```

#### Managing Multiple Clusters

```
Show me all available Kubernetes contexts.
```

```
Switch to the "production" context and list all services.
```

## Advanced Usage

### Working with Multiple Cloud Providers

The Kubernetes MCP server automatically detects the cloud provider of your Kubernetes cluster and adapts its behavior accordingly. It supports:

- AWS EKS (Amazon Elastic Kubernetes Service)
- Azure AKS (Azure Kubernetes Service)
- Google GKE (Google Kubernetes Engine)
- ROSA (Red Hat OpenShift Service on AWS)

To switch between clusters on different cloud providers, simply use the `set_context` tool with the appropriate context name from your kubeconfig.

### Scaling Node Pools

You can scale node pools on different cloud providers using the `exec_command` tool:

#### For AWS EKS:
```
Scale my EKS node group "workers" to 5 nodes.
```

#### For Azure AKS:
```
Scale my AKS node pool "nodepool1" to 3 nodes.
```

#### For Google GKE:
```
Add 2 more nodes to my GKE node pool "default-pool".
```

### Troubleshooting Common Issues

#### Pod Issues

```
Why is my pod "app-xyz" in CrashLoopBackOff state?
```

#### Deployment Problems

```
Why doesn't my deployment "frontend" have all replicas available?
```

#### Resource Constraints

```
Are there any resource constraints in my cluster?
```

## Development

### Project Structure

```
kubernetes-mcp-server/
├── kubernetes_mcp_server/
│   ├── __init__.py
│   ├── server.py        # MCP server implementation
│   └── k8s_client.py    # Kubernetes client implementation
├── tests/
│   └── test_server.py   # Tests for the MCP server
├── setup.py             # Package setup file
├── requirements.txt     # Package dependencies
└── README.md            # This file
```

### Running Tests

```bash
python -m unittest discover tests
```

### Building the Package

```bash
python setup.py sdist bdist_wheel
```

## Troubleshooting

### Common Issues

#### MCP Server Not Starting

If the MCP server fails to start, check:

1. Python version (should be 3.8+)
2. Required packages are installed
3. Kubeconfig file is valid and accessible
4. Permissions to access the Kubernetes API

#### Authentication Issues

If you encounter authentication issues:

1. Ensure your kubeconfig is up to date
2. Check if your cluster credentials are still valid
3. Try running `kubectl get nodes` to verify direct access works

#### Context Switching Problems

If context switching doesn't work:

1. Verify the context name exists in your kubeconfig
2. Check for typos in context names
3. Ensure you have permissions to access the target cluster

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The Kubernetes team for their excellent Python client
- The Model Context Protocol community for enabling AI assistants to interact with tools

## Runbook: Common Kubernetes Operations with MCP

### Cluster Management

#### Getting Cluster Information

```
Can you tell me about my Kubernetes cluster?
```

Response will include:
- Kubernetes version
- Cloud provider
- Number of nodes
- Number of namespaces
- Current context

#### Switching Contexts

```
Switch to the "production" context.
```

This will change the active context for subsequent operations.

### Resource Management

#### Creating Resources

```
Create a new namespace called "application".
```

```
Deploy this YAML manifest:
[paste YAML here]
```

#### Updating Resources

```
Update the deployment "frontend" to use image version 2.0.
```

```
Scale the deployment "api" to 5 replicas.
```

#### Deleting Resources

```
Delete the pod "crashed-pod" in namespace "default".
```

```
Remove the deployment "old-app" and all its resources.
```

### Monitoring and Troubleshooting

#### Viewing Logs

```
Show me the last 100 lines of logs from pod "api-server".
```

#### Executing Commands in Pods

```
Run "ls -la /app" in the "web-frontend" pod.
```

#### Checking Resource Usage

```
What's the CPU and memory usage across my nodes?
```

#### Diagnosing Issues

```
Why is my deployment "database" not ready?
```

```
Check if there are any pods in a non-running state.
```

### Advanced Operations

#### Working with Helm

```
List all Helm releases in the cluster.
```

```
Upgrade the "prometheus" Helm release to version 15.0.0.
```

#### Managing RBAC

```
Show me the service accounts in the "kube-system" namespace.
```

```
Create a new role binding for the "developer" service account.
```

#### Network Troubleshooting

```
Test connectivity from pod "frontend" to service "backend".
```

```
Show me all ingress resources in the cluster.
```

## Cloud Provider-Specific Operations

### AWS EKS

```
Scale my EKS node group to 5 nodes.
```

```
Update my EKS cluster to Kubernetes version 1.26.
```

### Azure AKS

```
Enable the monitoring add-on for my AKS cluster.
```

```
Show the available VM sizes for AKS nodes.
```

### Google GKE

```
Enable Workload Identity on my GKE cluster.
```

```
Create a new node pool with GPUs.
```

### Red Hat OpenShift (ROSA)

```
Show all routes in my OpenShift cluster.
```

```
Create a new project in OpenShift.

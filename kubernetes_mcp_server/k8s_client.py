"""
Kubernetes client module for interacting with Kubernetes clusters.

This module provides functionality to connect to and interact with Kubernetes clusters
using the active context from the user's kubeconfig file.
"""

import os
import json
import yaml
import base64
from typing import Dict, List, Any, Optional, Tuple, Union
from kubernetes import client, config
from kubernetes.client.rest import ApiException


class KubernetesClient:
    """Client for interacting with Kubernetes clusters using kubeconfig."""

    def __init__(self, context_name: Optional[str] = None):
        """
        Initialize the Kubernetes client using kubeconfig.

        Args:
            context_name: Optional name of the kubeconfig context to use.
                          If not provided, the active context from kubeconfig will be used.
        """
        self.api_client = None
        self.core_v1_api = None
        self.apps_v1_api = None
        self.batch_v1_api = None
        self.networking_v1_api = None
        self.rbac_v1_api = None
        self.custom_objects_api = None
        self.context_name = context_name
        self.current_namespace = "default"
        self.active_context_info = None
        
        # Load the configuration from kubeconfig
        self._load_config()

    def _load_config(self) -> None:
        """Load Kubernetes configuration from kubeconfig file."""
        try:
            # Try to load from default kubeconfig
            if self.context_name:
                config.load_kube_config(context=self.context_name)
            else:
                config.load_kube_config()
            
            # Create API clients
            self.api_client = client.ApiClient()
            self.core_v1_api = client.CoreV1Api(self.api_client)
            self.apps_v1_api = client.AppsV1Api(self.api_client)
            self.batch_v1_api = client.BatchV1Api(self.api_client)
            self.networking_v1_api = client.NetworkingV1Api(self.api_client)
            self.rbac_v1_api = client.RbacAuthorizationV1Api(self.api_client)
            self.custom_objects_api = client.CustomObjectsApi(self.api_client)
            
            # Get current context and namespace from config
            contexts, active_context = config.list_kube_config_contexts()
            if active_context:
                self.active_context_info = active_context
                self.current_namespace = active_context.get('context', {}).get('namespace', 'default')
            
        except Exception as e:
            raise Exception(f"Failed to load Kubernetes configuration from kubeconfig: {str(e)}")

    def set_context(self, context_name: str) -> None:
        """
        Set the Kubernetes context to use.

        Args:
            context_name: The name of the context from kubeconfig to use.
        """
        self.context_name = context_name
        self._load_config()

    def set_namespace(self, namespace: str) -> None:
        """
        Set the current namespace.

        Args:
            namespace: The namespace to use for subsequent operations.
        """
        self.current_namespace = namespace

    def get_contexts(self) -> List[Dict[str, Any]]:
        """
        Get available Kubernetes contexts from kubeconfig.

        Returns:
            List of context information dictionaries.
        """
        try:
            contexts, active_context = config.list_kube_config_contexts()
            result = []
            
            for ctx in contexts:
                context_info = {
                    "name": ctx["name"],
                    "cluster": ctx["context"]["cluster"],
                    "user": ctx["context"]["user"],
                    "is_active": ctx == active_context
                }
                if "namespace" in ctx["context"]:
                    context_info["namespace"] = ctx["context"]["namespace"]
                result.append(context_info)
            
            return result
        except Exception as e:
            raise Exception(f"Failed to get Kubernetes contexts from kubeconfig: {str(e)}")

    def get_namespaces(self) -> List[Dict[str, Any]]:
        """
        Get all namespaces in the cluster.

        Returns:
            List of namespace information dictionaries.
        """
        try:
            namespaces = self.core_v1_api.list_namespace()
            return [
                {
                    "name": ns.metadata.name,
                    "status": ns.status.phase,
                    "creation_timestamp": ns.metadata.creation_timestamp.isoformat() 
                        if ns.metadata.creation_timestamp else None
                }
                for ns in namespaces.items
            ]
        except ApiException as e:
            raise Exception(f"Failed to get namespaces: {str(e)}")

    def get_pods(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all pods in the specified namespace.

        Args:
            namespace: The namespace to get pods from. If not provided, uses the current namespace.

        Returns:
            List of pod information dictionaries.
        """
        namespace = namespace or self.current_namespace
        try:
            pods = self.core_v1_api.list_namespaced_pod(namespace)
            return [
                {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "ip": pod.status.pod_ip,
                    "node": pod.spec.node_name,
                    "creation_timestamp": pod.metadata.creation_timestamp.isoformat() 
                        if pod.metadata.creation_timestamp else None
                }
                for pod in pods.items
            ]
        except ApiException as e:
            raise Exception(f"Failed to get pods in namespace {namespace}: {str(e)}")

    def get_pod_logs(self, pod_name: str, namespace: Optional[str] = None, 
                    container: Optional[str] = None, tail_lines: Optional[int] = None) -> str:
        """
        Get logs from a pod.

        Args:
            pod_name: Name of the pod.
            namespace: The namespace the pod is in. If not provided, uses the current namespace.
            container: Name of the container to get logs from. If not provided, uses the first container.
            tail_lines: Number of lines to get from the end of the logs. If not provided, gets all logs.

        Returns:
            Pod logs as a string.
        """
        namespace = namespace or self.current_namespace
        try:
            return self.core_v1_api.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                container=container,
                tail_lines=tail_lines
            )
        except ApiException as e:
            raise Exception(f"Failed to get logs for pod {pod_name} in namespace {namespace}: {str(e)}")

    def get_deployments(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all deployments in the specified namespace.

        Args:
            namespace: The namespace to get deployments from. If not provided, uses the current namespace.

        Returns:
            List of deployment information dictionaries.
        """
        namespace = namespace or self.current_namespace
        try:
            deployments = self.apps_v1_api.list_namespaced_deployment(namespace)
            return [
                {
                    "name": dep.metadata.name,
                    "namespace": dep.metadata.namespace,
                    "replicas": dep.spec.replicas,
                    "available_replicas": dep.status.available_replicas,
                    "creation_timestamp": dep.metadata.creation_timestamp.isoformat() 
                        if dep.metadata.creation_timestamp else None
                }
                for dep in deployments.items
            ]
        except ApiException as e:
            raise Exception(f"Failed to get deployments in namespace {namespace}: {str(e)}")

    def get_services(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all services in the specified namespace.

        Args:
            namespace: The namespace to get services from. If not provided, uses the current namespace.

        Returns:
            List of service information dictionaries.
        """
        namespace = namespace or self.current_namespace
        try:
            services = self.core_v1_api.list_namespaced_service(namespace)
            return [
                {
                    "name": svc.metadata.name,
                    "namespace": svc.metadata.namespace,
                    "type": svc.spec.type,
                    "cluster_ip": svc.spec.cluster_ip,
                    "ports": [
                        {
                            "name": port.name,
                            "port": port.port,
                            "target_port": port.target_port,
                            "protocol": port.protocol
                        }
                        for port in svc.spec.ports
                    ] if svc.spec.ports else [],
                    "creation_timestamp": svc.metadata.creation_timestamp.isoformat() 
                        if svc.metadata.creation_timestamp else None
                }
                for svc in services.items
            ]
        except ApiException as e:
            raise Exception(f"Failed to get services in namespace {namespace}: {str(e)}")

    def get_configmaps(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all configmaps in the specified namespace.

        Args:
            namespace: The namespace to get configmaps from. If not provided, uses the current namespace.

        Returns:
            List of configmap information dictionaries.
        """
        namespace = namespace or self.current_namespace
        try:
            configmaps = self.core_v1_api.list_namespaced_config_map(namespace)
            return [
                {
                    "name": cm.metadata.name,
                    "namespace": cm.metadata.namespace,
                    "data_keys": list(cm.data.keys()) if cm.data else [],
                    "creation_timestamp": cm.metadata.creation_timestamp.isoformat() 
                        if cm.metadata.creation_timestamp else None
                }
                for cm in configmaps.items
            ]
        except ApiException as e:
            raise Exception(f"Failed to get configmaps in namespace {namespace}: {str(e)}")

    def get_secrets(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all secrets in the specified namespace.

        Args:
            namespace: The namespace to get secrets from. If not provided, uses the current namespace.

        Returns:
            List of secret information dictionaries.
        """
        namespace = namespace or self.current_namespace
        try:
            secrets = self.core_v1_api.list_namespaced_secret(namespace)
            return [
                {
                    "name": secret.metadata.name,
                    "namespace": secret.metadata.namespace,
                    "type": secret.type,
                    "data_keys": list(secret.data.keys()) if secret.data else [],
                    "creation_timestamp": secret.metadata.creation_timestamp.isoformat() 
                        if secret.metadata.creation_timestamp else None
                }
                for secret in secrets.items
            ]
        except ApiException as e:
            raise Exception(f"Failed to get secrets in namespace {namespace}: {str(e)}")

    def get_nodes(self) -> List[Dict[str, Any]]:
        """
        Get all nodes in the cluster.

        Returns:
            List of node information dictionaries.
        """
        try:
            nodes = self.core_v1_api.list_node()
            return [
                {
                    "name": node.metadata.name,
                    "status": [cond.type for cond in node.status.conditions if cond.status == "True"],
                    "kubelet_version": node.status.node_info.kubelet_version,
                    "os_image": node.status.node_info.os_image,
                    "addresses": [
                        {"type": addr.type, "address": addr.address}
                        for addr in node.status.addresses
                    ] if node.status.addresses else [],
                    "creation_timestamp": node.metadata.creation_timestamp.isoformat() 
                        if node.metadata.creation_timestamp else None
                }
                for node in nodes.items
            ]
        except ApiException as e:
            raise Exception(f"Failed to get nodes: {str(e)}")

    def create_from_yaml(self, yaml_content: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Create Kubernetes resources from YAML content.

        Args:
            yaml_content: YAML content defining Kubernetes resources.
            namespace: The namespace to create resources in. If not provided, uses the current namespace.

        Returns:
            Dictionary with information about created resources.
        """
        namespace = namespace or self.current_namespace
        try:
            # Parse YAML content
            resources = list(yaml.safe_load_all(yaml_content))
            results = []
            
            for resource in resources:
                # Set namespace if not specified in the resource
                if "metadata" in resource and "namespace" not in resource["metadata"]:
                    resource["metadata"]["namespace"] = namespace
                
                # Determine the API to use based on resource kind
                kind = resource.get("kind", "")
                api_version = resource.get("apiVersion", "")
                
                # Create the resource using the appropriate API
                if kind.lower() == "pod" and api_version == "v1":
                    resp = self.core_v1_api.create_namespaced_pod(
                        namespace=resource["metadata"]["namespace"],
                        body=resource
                    )
                    results.append({"kind": kind, "name": resp.metadata.name, "created": True})
                
                elif kind.lower() == "deployment" and api_version == "apps/v1":
                    resp = self.apps_v1_api.create_namespaced_deployment(
                        namespace=resource["metadata"]["namespace"],
                        body=resource
                    )
                    results.append({"kind": kind, "name": resp.metadata.name, "created": True})
                
                elif kind.lower() == "service" and api_version == "v1":
                    resp = self.core_v1_api.create_namespaced_service(
                        namespace=resource["metadata"]["namespace"],
                        body=resource
                    )
                    results.append({"kind": kind, "name": resp.metadata.name, "created": True})
                
                elif kind.lower() == "configmap" and api_version == "v1":
                    resp = self.core_v1_api.create_namespaced_config_map(
                        namespace=resource["metadata"]["namespace"],
                        body=resource
                    )
                    results.append({"kind": kind, "name": resp.metadata.name, "created": True})
                
                elif kind.lower() == "secret" and api_version == "v1":
                    resp = self.core_v1_api.create_namespaced_secret(
                        namespace=resource["metadata"]["namespace"],
                        body=resource
                    )
                    results.append({"kind": kind, "name": resp.metadata.name, "created": True})
                
                elif kind.lower() == "namespace" and api_version == "v1":
                    resp = self.core_v1_api.create_namespace(body=resource)
                    results.append({"kind": kind, "name": resp.metadata.name, "created": True})
                
                else:
                    # For custom resources or other types
                    group, version = api_version.split("/") if "/" in api_version else ("", api_version)
                    plural = f"{kind.lower()}s"  # Simple pluralization, may need to be more sophisticated
                    
                    if "metadata" in resource and "namespace" in resource["metadata"]:
                        resp = self.custom_objects_api.create_namespaced_custom_object(
                            group=group,
                            version=version,
                            namespace=resource["metadata"]["namespace"],
                            plural=plural,
                            body=resource
                        )
                    else:
                        resp = self.custom_objects_api.create_cluster_custom_object(
                            group=group,
                            version=version,
                            plural=plural,
                            body=resource
                        )
                    
                    results.append({
                        "kind": kind, 
                        "name": resource["metadata"]["name"], 
                        "created": True
                    })
            
            return {"created_resources": results}
        
        except ApiException as e:
            raise Exception(f"Failed to create resources from YAML: {str(e)}")
        except yaml.YAMLError as e:
            raise Exception(f"Invalid YAML content: {str(e)}")

    def delete_resource(self, kind: str, name: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a Kubernetes resource.

        Args:
            kind: Kind of resource to delete (e.g., "Pod", "Deployment").
            name: Name of the resource.
            namespace: The namespace the resource is in. If not provided, uses the current namespace.

        Returns:
            Dictionary with information about the deleted resource.
        """
        namespace = namespace or self.current_namespace
        try:
            # Determine the API to use based on resource kind
            kind = kind.lower()
            
            if kind == "pod":
                self.core_v1_api.delete_namespaced_pod(name=name, namespace=namespace)
            
            elif kind == "deployment":
                self.apps_v1_api.delete_namespaced_deployment(name=name, namespace=namespace)
            
            elif kind == "service":
                self.core_v1_api.delete_namespaced_service(name=name, namespace=namespace)
            
            elif kind == "configmap":
                self.core_v1_api.delete_namespaced_config_map(name=name, namespace=namespace)
            
            elif kind == "secret":
                self.core_v1_api.delete_namespaced_secret(name=name, namespace=namespace)
            
            elif kind == "namespace":
                self.core_v1_api.delete_namespace(name=name)
            
            else:
                # For custom resources or other types, would need more information
                raise Exception(f"Deleting resource of kind {kind} is not implemented")
            
            return {"kind": kind, "name": name, "deleted": True}
        
        except ApiException as e:
            raise Exception(f"Failed to delete {kind} {name} in namespace {namespace}: {str(e)}")

    def update_from_yaml(self, yaml_content: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Update Kubernetes resources from YAML content.

        Args:
            yaml_content: YAML content defining Kubernetes resources.
            namespace: The namespace to update resources in. If not provided, uses the current namespace.

        Returns:
            Dictionary with information about updated resources.
        """
        namespace = namespace or self.current_namespace
        try:
            # Parse YAML content
            resources = list(yaml.safe_load_all(yaml_content))
            results = []
            
            for resource in resources:
                # Set namespace if not specified in the resource
                if "metadata" in resource and "namespace" not in resource["metadata"]:
                    resource["metadata"]["namespace"] = namespace
                
                # Determine the API to use based on resource kind
                kind = resource.get("kind", "")
                api_version = resource.get("apiVersion", "")
                name = resource["metadata"]["name"]
                ns = resource["metadata"]["namespace"]
                
                # Update the resource using the appropriate API
                if kind.lower() == "pod" and api_version == "v1":
                    resp = self.core_v1_api.replace_namespaced_pod(
                        name=name,
                        namespace=ns,
                        body=resource
                    )
                    results.append({"kind": kind, "name": resp.metadata.name, "updated": True})
                
                elif kind.lower() == "deployment" and api_version == "apps/v1":
                    resp = self.apps_v1_api.replace_namespaced_deployment(
                        name=name,
                        namespace=ns,
                        body=resource
                    )
                    results.append({"kind": kind, "name": resp.metadata.name, "updated": True})
                
                elif kind.lower() == "service" and api_version == "v1":
                    resp = self.core_v1_api.replace_namespaced_service(
                        name=name,
                        namespace=ns,
                        body=resource
                    )
                    results.append({"kind": kind, "name": resp.metadata.name, "updated": True})
                
                elif kind.lower() == "configmap" and api_version == "v1":
                    resp = self.core_v1_api.replace_namespaced_config_map(
                        name=name,
                        namespace=ns,
                        body=resource
                    )
                    results.append({"kind": kind, "name": resp.metadata.name, "updated": True})
                
                elif kind.lower() == "secret" and api_version == "v1":
                    resp = self.core_v1_api.replace_namespaced_secret(
                        name=name,
                        namespace=ns,
                        body=resource
                    )
                    results.append({"kind": kind, "name": resp.metadata.name, "updated": True})
                
                else:
                    # For custom resources or other types
                    group, version = api_version.split("/") if "/" in api_version else ("", api_version)
                    plural = f"{kind.lower()}s"  # Simple pluralization, may need to be more sophisticated
                    
                    if "metadata" in resource and "namespace" in resource["metadata"]:
                        resp = self.custom_objects_api.replace_namespaced_custom_object(
                            group=group,
                            version=version,
                            namespace=ns,
                            plural=plural,
                            name=name,
                            body=resource
                        )
                    else:
                        resp = self.custom_objects_api.replace_cluster_custom_object(
                            group=group,
                            version=version,
                            plural=plural,
                            name=name,
                            body=resource
                        )
                    
                    results.append({
                        "kind": kind, 
                        "name": name, 
                        "updated": True
                    })
            
            return {"updated_resources": results}
        
        except ApiException as e:
            raise Exception(f"Failed to update resources from YAML: {str(e)}")
        except yaml.YAMLError as e:
            raise Exception(f"Invalid YAML content: {str(e)}")

    def get_resource_yaml(self, kind: str, name: str, namespace: Optional[str] = None) -> str:
        """
        Get YAML representation of a Kubernetes resource.

        Args:
            kind: Kind of resource to get (e.g., "Pod", "Deployment").
            name: Name of the resource.
            namespace: The namespace the resource is in. If not provided, uses the current namespace.

        Returns:
            YAML representation of the resource.
        """
        namespace = namespace or self.current_namespace
        try:
            # Determine the API to use based on resource kind
            kind = kind.lower()
            
            if kind == "pod":
                resource = self.core_v1_api.read_namespaced_pod(name=name, namespace=namespace)
            
            elif kind == "deployment":
                resource = self.apps_v1_api.read_namespaced_deployment(name=name, namespace=namespace)
            
            elif kind == "service":
                resource = self.core_v1_api.read_namespaced_service(name=name, namespace=namespace)
            
            elif kind == "configmap":
                resource = self.core_v1_api.read_namespaced_config_map(name=name, namespace=namespace)
            
            elif kind == "secret":
                resource = self.core_v1_api.read_namespaced_secret(name=name, namespace=namespace)
            
            elif kind == "namespace":
                resource = self.core_v1_api.read_namespace(name=name)
            
            else:
                # For custom resources or other types, would need more information
                raise Exception(f"Getting YAML for resource of kind {kind} is not implemented")
            
            # Convert to dict and then to YAML
            resource_dict = client.ApiClient().sanitize_for_serialization(resource)
            return yaml.dump(resource_dict)
        
        except ApiException as e:
            raise Exception(f"Failed to get {kind} {name} in namespace {namespace}: {str(e)}")

    def exec_command(self, pod_name: str, command: List[str], namespace: Optional[str] = None, 
                    container: Optional[str] = None) -> str:
        """
        Execute a command in a pod.

        Args:
            pod_name: Name of the pod.
            command: Command to execute as a list of strings.
            namespace: The namespace the pod is in. If not provided, uses the current namespace.
            container: Name of the container to execute the command in. If not provided, uses the first container.

        Returns:
            Command output as a string.
        """
        namespace = namespace or self.current_namespace
        try:
            # Get the pod to find the container name if not provided
            if not container:
                pod = self.core_v1_api.read_namespaced_pod(name=pod_name, namespace=namespace)
                if pod.spec.containers:
                    container = pod.spec.containers[0].name
                else:
                    raise Exception(f"No containers found in pod {pod_name}")
            
            # Execute the command
            exec_command = ['/bin/sh', '-c', ' '.join(command)]
            resp = client.CoreV1Api().connect_get_namespaced_pod_exec(
                name=pod_name,
                namespace=namespace,
                container=container,
                command=exec_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False
            )
            
            return resp
        
        except ApiException as e:
            raise Exception(f"Failed to execute command in pod {pod_name}: {str(e)}")

    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get information about the current Kubernetes cluster.

        Returns:
            Dictionary with cluster information.
        """
        try:
            # Get version info
            version_info = client.VersionApi().get_code()
            
            # Get current context info
            contexts, active_context = config.list_kube_config_contexts()
            
            # Get node count
            nodes = self.core_v1_api.list_node()
            node_count = len(nodes.items)
            
            # Get namespace count
            namespaces = self.core_v1_api.list_namespace()
            namespace_count = len(namespaces.items)
            
            # Determine cloud provider if possible
            cloud_provider = "unknown"
            for node in nodes.items:
                if node.spec.provider_id:
                    if node.spec.provider_id.startswith("aws"):
                        cloud_provider = "AWS EKS"
                        break
                    elif node.spec.provider_id.startswith("azure"):
                        cloud_provider = "Azure AKS"
                        break
                    elif node.spec.provider_id.startswith("gce"):
                        cloud_provider = "Google GKE"
                        break
                
                # Check labels for cloud provider hints
                if node.metadata.labels:
                    if any(label.startswith("eks.amazonaws.com") for label in node.metadata.labels):
                        cloud_provider = "AWS EKS"
                        break
                    elif any(label.startswith("kubernetes.azure.com") for label in node.metadata.labels):
                        cloud_provider = "Azure AKS"
                        break
                    elif any(label.startswith("cloud.google.com") for label in node.metadata.labels):
                        cloud_provider = "Google GKE"
                        break
                    elif any(label.startswith("openshift.io") for label in node.metadata.labels):
                        cloud_provider = "ROSA (Red Hat OpenShift on AWS)"
                        break
            
            return {
                "version": {
                    "major": version_info.major,
                    "minor": version_info.minor,
                    "git_version": version_info.git_version,
                    "platform": version_info.platform
                },
                "context": {
                    "name": active_context["name"],
                    "cluster": active_context["context"]["cluster"],
                    "user": active_context["context"]["user"]
                },
                "node_count": node_count,
                "namespace_count": namespace_count,
                "cloud_provider": cloud_provider
            }
        
        except ApiException as e:
            raise Exception(f"Failed to get cluster info: {str(e)}")

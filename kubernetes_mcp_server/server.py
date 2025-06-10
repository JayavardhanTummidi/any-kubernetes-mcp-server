#!/usr/bin/env python3
"""
Kubernetes MCP Server - A Model Context Protocol server for Kubernetes operations.

This module implements the MCP server for Kubernetes operations, providing tools
and resources for interacting with Kubernetes clusters.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union

# Simple MCP server implementation
class Server:
    """Simple MCP server implementation."""
    
    def __init__(self, info, capabilities):
        """Initialize the server."""
        self.info = info
        self.capabilities = capabilities
        self.request_handlers = {}
        self.onerror = None
    
    def set_request_handler(self, schema, handler):
        """Set a request handler for a specific schema."""
        self.request_handlers[schema.__name__] = handler
    
    async def connect(self, transport):
        """Connect to the transport."""
        await transport.connect(self)

class StdioServerTransport:
    """Simple stdio server transport."""
    
    async def connect(self, server):
        """Connect to the server."""
        print("Connected to stdio transport", file=sys.stderr)
        # In a real implementation, this would handle the stdio communication

# MCP types
class ListResourcesRequestSchema:
    """List resources request schema."""
    pass

class ListResourceTemplatesRequestSchema:
    """List resource templates request schema."""
    pass

class ReadResourceRequestSchema:
    """Read resource request schema."""
    pass

class ListToolsRequestSchema:
    """List tools request schema."""
    pass

class CallToolRequestSchema:
    """Call tool request schema."""
    pass

class ErrorCode:
    """Error codes."""
    InvalidRequest = "invalid_request"
    InvalidParams = "invalid_params"
    MethodNotFound = "method_not_found"
    InternalError = "internal_error"

class McpError(Exception):
    """MCP error."""
    
    def __init__(self, code, message):
        """Initialize the error."""
        self.code = code
        self.message = message
        super().__init__(message)

# Local imports
from kubernetes_mcp_server.k8s_client import KubernetesClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/kubernetes-mcp-server.log"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("kubernetes-mcp-server")


class KubernetesMcpServer:
    """MCP server for Kubernetes operations."""

    def __init__(self):
        """Initialize the Kubernetes MCP server."""
        self.server = Server(
            {
                "name": "kubernetes-mcp-server",
                "version": "0.1.0",
            },
            {
                "capabilities": {
                    "resources": {},
                    "tools": {},
                },
            }
        )
        
        # Initialize Kubernetes client
        self.k8s_client = KubernetesClient()
        
        # Set up request handlers
        self._setup_resource_handlers()
        self._setup_tool_handlers()
        
        # Error handling
        self.server.onerror = lambda error: logger.error(f"[MCP Error] {error}")
        
    def _setup_resource_handlers(self):
        """Set up resource handlers for the MCP server."""
        # List available resources
        self.server.set_request_handler(ListResourcesRequestSchema, self._handle_list_resources)
        
        # List resource templates
        self.server.set_request_handler(ListResourceTemplatesRequestSchema, self._handle_list_resource_templates)
        
        # Read resource
        self.server.set_request_handler(ReadResourceRequestSchema, self._handle_read_resource)
    
    def _setup_tool_handlers(self):
        """Set up tool handlers for the MCP server."""
        # List available tools
        self.server.set_request_handler(ListToolsRequestSchema, self._handle_list_tools)
        
        # Call tool
        self.server.set_request_handler(CallToolRequestSchema, self._handle_call_tool)
    
    async def _handle_list_resources(self, request):
        """
        Handle request to list available resources.
        
        Returns:
            Dictionary with list of available resources.
        """
        try:
            # Get current context
            contexts = self.k8s_client.get_contexts()
            active_context = next((ctx for ctx in contexts if ctx.get("is_active")), None)
            
            if not active_context:
                return {"resources": []}
            
            # Create resources for the active context
            resources = [
                {
                    "uri": f"k8s://{active_context['name']}/info",
                    "name": f"Kubernetes cluster info for {active_context['name']}",
                    "mimeType": "application/json",
                    "description": "Information about the current Kubernetes cluster"
                }
            ]
            
            return {"resources": resources}
        except Exception as e:
            logger.error(f"Error listing resources: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Failed to list resources: {str(e)}")
    
    async def _handle_list_resource_templates(self, request):
        """
        Handle request to list available resource templates.
        
        Returns:
            Dictionary with list of available resource templates.
        """
        try:
            # Define resource templates
            resource_templates = [
                {
                    "uriTemplate": "k8s://{context}/namespaces",
                    "name": "Kubernetes namespaces",
                    "mimeType": "application/json",
                    "description": "List of namespaces in the specified Kubernetes context"
                },
                {
                    "uriTemplate": "k8s://{context}/namespace/{namespace}/pods",
                    "name": "Kubernetes pods in namespace",
                    "mimeType": "application/json",
                    "description": "List of pods in the specified namespace"
                },
                {
                    "uriTemplate": "k8s://{context}/namespace/{namespace}/deployments",
                    "name": "Kubernetes deployments in namespace",
                    "mimeType": "application/json",
                    "description": "List of deployments in the specified namespace"
                },
                {
                    "uriTemplate": "k8s://{context}/namespace/{namespace}/services",
                    "name": "Kubernetes services in namespace",
                    "mimeType": "application/json",
                    "description": "List of services in the specified namespace"
                },
                {
                    "uriTemplate": "k8s://{context}/namespace/{namespace}/configmaps",
                    "name": "Kubernetes configmaps in namespace",
                    "mimeType": "application/json",
                    "description": "List of configmaps in the specified namespace"
                },
                {
                    "uriTemplate": "k8s://{context}/namespace/{namespace}/secrets",
                    "name": "Kubernetes secrets in namespace",
                    "mimeType": "application/json",
                    "description": "List of secrets in the specified namespace"
                },
                {
                    "uriTemplate": "k8s://{context}/nodes",
                    "name": "Kubernetes nodes",
                    "mimeType": "application/json",
                    "description": "List of nodes in the cluster"
                },
                {
                    "uriTemplate": "k8s://{context}/namespace/{namespace}/pod/{pod}/logs",
                    "name": "Kubernetes pod logs",
                    "mimeType": "text/plain",
                    "description": "Logs from the specified pod"
                },
                {
                    "uriTemplate": "k8s://{context}/namespace/{namespace}/resource/{kind}/{name}",
                    "name": "Kubernetes resource YAML",
                    "mimeType": "application/yaml",
                    "description": "YAML representation of the specified Kubernetes resource"
                }
            ]
            
            return {"resourceTemplates": resource_templates}
        except Exception as e:
            logger.error(f"Error listing resource templates: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Failed to list resource templates: {str(e)}")
    
    async def _handle_read_resource(self, request):
        """
        Handle request to read a resource.
        
        Args:
            request: The MCP request object.
        
        Returns:
            Dictionary with resource contents.
        """
        try:
            uri = request.params.uri
            
            # Parse the URI
            if not uri.startswith("k8s://"):
                raise McpError(ErrorCode.InvalidRequest, f"Invalid URI scheme: {uri}")
            
            # Remove the scheme and split the path
            path = uri[6:]  # Remove "k8s://"
            parts = path.split("/")
            
            if len(parts) < 2:
                raise McpError(ErrorCode.InvalidRequest, f"Invalid URI format: {uri}")
            
            context_name = parts[0]
            resource_type = parts[1]
            
            # Set the context if it's not the current one
            contexts = self.k8s_client.get_contexts()
            active_context = next((ctx for ctx in contexts if ctx.get("is_active")), None)
            
            if not active_context or active_context["name"] != context_name:
                # Check if the requested context exists
                if not any(ctx["name"] == context_name for ctx in contexts):
                    raise McpError(ErrorCode.InvalidRequest, f"Context not found: {context_name}")
                
                # Set the context
                self.k8s_client.set_context(context_name)
            
            # Handle different resource types
            if resource_type == "info":
                # Get cluster info
                cluster_info = self.k8s_client.get_cluster_info()
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(cluster_info, indent=2)
                        }
                    ]
                }
            
            elif resource_type == "namespaces":
                # Get namespaces
                namespaces = self.k8s_client.get_namespaces()
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(namespaces, indent=2)
                        }
                    ]
                }
            
            elif resource_type == "nodes":
                # Get nodes
                nodes = self.k8s_client.get_nodes()
                return {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(nodes, indent=2)
                        }
                    ]
                }
            
            elif resource_type == "namespace" and len(parts) >= 4:
                namespace = parts[2]
                resource_subtype = parts[3]
                
                if resource_subtype == "pods":
                    # Get pods in namespace
                    pods = self.k8s_client.get_pods(namespace)
                    return {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "application/json",
                                "text": json.dumps(pods, indent=2)
                            }
                        ]
                    }
                
                elif resource_subtype == "deployments":
                    # Get deployments in namespace
                    deployments = self.k8s_client.get_deployments(namespace)
                    return {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "application/json",
                                "text": json.dumps(deployments, indent=2)
                            }
                        ]
                    }
                
                elif resource_subtype == "services":
                    # Get services in namespace
                    services = self.k8s_client.get_services(namespace)
                    return {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "application/json",
                                "text": json.dumps(services, indent=2)
                            }
                        ]
                    }
                
                elif resource_subtype == "configmaps":
                    # Get configmaps in namespace
                    configmaps = self.k8s_client.get_configmaps(namespace)
                    return {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "application/json",
                                "text": json.dumps(configmaps, indent=2)
                            }
                        ]
                    }
                
                elif resource_subtype == "secrets":
                    # Get secrets in namespace
                    secrets = self.k8s_client.get_secrets(namespace)
                    return {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "application/json",
                                "text": json.dumps(secrets, indent=2)
                            }
                        ]
                    }
                
                elif resource_subtype == "pod" and len(parts) >= 6 and parts[5] == "logs":
                    # Get pod logs
                    pod_name = parts[4]
                    logs = self.k8s_client.get_pod_logs(pod_name, namespace)
                    return {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "text/plain",
                                "text": logs
                            }
                        ]
                    }
                
                elif resource_subtype == "resource" and len(parts) >= 6:
                    # Get resource YAML
                    kind = parts[4]
                    name = parts[5]
                    yaml_content = self.k8s_client.get_resource_yaml(kind, name, namespace)
                    return {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "application/yaml",
                                "text": yaml_content
                            }
                        ]
                    }
            
            # If we get here, the URI format is not recognized
            raise McpError(ErrorCode.InvalidRequest, f"Invalid URI format: {uri}")
        
        except McpError:
            # Re-raise MCP errors
            raise
        except Exception as e:
            logger.error(f"Error reading resource: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Failed to read resource: {str(e)}")
    
    async def _handle_list_tools(self, request):
        """
        Handle request to list available tools.
        
        Returns:
            Dictionary with list of available tools.
        """
        try:
            # Define tools
            tools = [
                {
                    "name": "get_cluster_info",
                    "description": "Get information about the current Kubernetes cluster",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        }
                    }
                },
                {
                    "name": "get_contexts",
                    "description": "Get available Kubernetes contexts from kubeconfig",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "set_context",
                    "description": "Set the Kubernetes context to use",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use"
                            }
                        },
                        "required": ["context"]
                    }
                },
                {
                    "name": "get_namespaces",
                    "description": "Get all namespaces in the cluster",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        }
                    }
                },
                {
                    "name": "get_pods",
                    "description": "Get all pods in the specified namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {
                                "type": "string",
                                "description": "Namespace to get pods from. If not provided, uses the current namespace."
                            },
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        }
                    }
                },
                {
                    "name": "get_pod_logs",
                    "description": "Get logs from a pod",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "pod_name": {
                                "type": "string",
                                "description": "Name of the pod"
                            },
                            "namespace": {
                                "type": "string",
                                "description": "Namespace the pod is in. If not provided, uses the current namespace."
                            },
                            "container": {
                                "type": "string",
                                "description": "Name of the container to get logs from. If not provided, uses the first container."
                            },
                            "tail_lines": {
                                "type": "integer",
                                "description": "Number of lines to get from the end of the logs. If not provided, gets all logs."
                            },
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        },
                        "required": ["pod_name"]
                    }
                },
                {
                    "name": "get_deployments",
                    "description": "Get all deployments in the specified namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {
                                "type": "string",
                                "description": "Namespace to get deployments from. If not provided, uses the current namespace."
                            },
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        }
                    }
                },
                {
                    "name": "get_services",
                    "description": "Get all services in the specified namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {
                                "type": "string",
                                "description": "Namespace to get services from. If not provided, uses the current namespace."
                            },
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        }
                    }
                },
                {
                    "name": "get_configmaps",
                    "description": "Get all configmaps in the specified namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {
                                "type": "string",
                                "description": "Namespace to get configmaps from. If not provided, uses the current namespace."
                            },
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        }
                    }
                },
                {
                    "name": "get_secrets",
                    "description": "Get all secrets in the specified namespace",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "namespace": {
                                "type": "string",
                                "description": "Namespace to get secrets from. If not provided, uses the current namespace."
                            },
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        }
                    }
                },
                {
                    "name": "get_nodes",
                    "description": "Get all nodes in the cluster",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        }
                    }
                },
                {
                    "name": "create_from_yaml",
                    "description": "Create Kubernetes resources from YAML content",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "yaml_content": {
                                "type": "string",
                                "description": "YAML content defining Kubernetes resources"
                            },
                            "namespace": {
                                "type": "string",
                                "description": "Namespace to create resources in. If not provided, uses the current namespace."
                            },
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        },
                        "required": ["yaml_content"]
                    }
                },
                {
                    "name": "update_from_yaml",
                    "description": "Update Kubernetes resources from YAML content",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "yaml_content": {
                                "type": "string",
                                "description": "YAML content defining Kubernetes resources"
                            },
                            "namespace": {
                                "type": "string",
                                "description": "Namespace to update resources in. If not provided, uses the current namespace."
                            },
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        },
                        "required": ["yaml_content"]
                    }
                },
                {
                    "name": "delete_resource",
                    "description": "Delete a Kubernetes resource",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "kind": {
                                "type": "string",
                                "description": "Kind of resource to delete (e.g., 'Pod', 'Deployment')"
                            },
                            "name": {
                                "type": "string",
                                "description": "Name of the resource"
                            },
                            "namespace": {
                                "type": "string",
                                "description": "Namespace the resource is in. If not provided, uses the current namespace."
                            },
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        },
                        "required": ["kind", "name"]
                    }
                },
                {
                    "name": "get_resource_yaml",
                    "description": "Get YAML representation of a Kubernetes resource",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "kind": {
                                "type": "string",
                                "description": "Kind of resource to get (e.g., 'Pod', 'Deployment')"
                            },
                            "name": {
                                "type": "string",
                                "description": "Name of the resource"
                            },
                            "namespace": {
                                "type": "string",
                                "description": "Namespace the resource is in. If not provided, uses the current namespace."
                            },
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        },
                        "required": ["kind", "name"]
                    }
                },
                {
                    "name": "exec_command",
                    "description": "Execute a command in a pod",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "pod_name": {
                                "type": "string",
                                "description": "Name of the pod"
                            },
                            "command": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "Command to execute as a list of strings"
                            },
                            "namespace": {
                                "type": "string",
                                "description": "Namespace the pod is in. If not provided, uses the current namespace."
                            },
                            "container": {
                                "type": "string",
                                "description": "Name of the container to execute the command in. If not provided, uses the first container."
                            },
                            "context": {
                                "type": "string",
                                "description": "Name of the Kubernetes context to use. If not provided, uses the current context."
                            }
                        },
                        "required": ["pod_name", "command"]
                    }
                }
            ]
            
            return {"tools": tools}
        except Exception as e:
            logger.error(f"Error listing tools: {str(e)}")
            raise McpError(ErrorCode.InternalError, f"Failed to list tools: {str(e)}")
    
    async def _handle_call_tool(self, request):
        """
        Handle request to call a tool.
        
        Args:
            request: The MCP request object.
        
        Returns:
            Dictionary with tool call result.
        """
        try:
            tool_name = request.params.name
            arguments = request.params.arguments
            
            # Set context if provided
            if "context" in arguments:
                context = arguments.pop("context")
                if context:
                    self.k8s_client.set_context(context)
            
            # Call the appropriate method based on the tool name
            if tool_name == "get_cluster_info":
                result = self.k8s_client.get_cluster_info()
            
            elif tool_name == "get_contexts":
                result = self.k8s_client.get_contexts()
            
            elif tool_name == "set_context":
                if "context" not in arguments:
                    raise McpError(ErrorCode.InvalidParams, "Missing required parameter: context")
                
                self.k8s_client.set_context(arguments["context"])
                result = {"success": True, "message": f"Context set to {arguments['context']}"}
            
            elif tool_name == "get_namespaces":
                result = self.k8s_client.get_namespaces()
            
            elif tool_name == "get_pods":
                namespace = arguments.get("namespace")
                result = self.k8s_client.get_pods(namespace)
            
            elif tool_name == "get_pod_logs":
                if "pod_name" not in arguments:
                    raise McpError(ErrorCode.InvalidParams, "Missing required parameter: pod_name")
                
                pod_name = arguments["pod_name"]
                namespace = arguments.get("namespace")
                container = arguments.get("container")
                tail_lines = arguments.get("tail_lines")
                
                result = self.k8s_client.get_pod_logs(pod_name, namespace, container, tail_lines)
            
            elif tool_name == "get_deployments":
                namespace = arguments.get("namespace")
                result = self.k8s_client.get_deployments(namespace)
            
            elif tool_name == "get_services":
                namespace = arguments.get("namespace")
                result = self.k8s_client.get_services(namespace)
            
            elif tool_name == "get_configmaps":
                namespace = arguments.get("namespace")
                result = self.k8s_client.get_configmaps(namespace)
            
            elif tool_name == "get_secrets":
                namespace = arguments.get("namespace")
                result = self.k8s_client.get_secrets(namespace)
            
            elif tool_name == "get_nodes":
                result = self.k8s_client.get_nodes()
            
            elif tool_name == "create_from_yaml":
                if "yaml_content" not in arguments:
                    raise McpError(ErrorCode.InvalidParams, "Missing required parameter: yaml_content")
                
                yaml_content = arguments["yaml_content"]
                namespace = arguments.get("namespace")
                
                result = self.k8s_client.create_from_yaml(yaml_content, namespace)
            
            elif tool_name == "update_from_yaml":
                if "yaml_content" not in arguments:
                    raise McpError(ErrorCode.InvalidParams, "Missing required parameter: yaml_content")
                
                yaml_content = arguments["yaml_content"]
                namespace = arguments.get("namespace")
                
                result = self.k8s_client.update_from_yaml(yaml_content, namespace)
            
            elif tool_name == "delete_resource":
                if "kind" not in arguments:
                    raise McpError(ErrorCode.InvalidParams, "Missing required parameter: kind")
                if "name" not in arguments:
                    raise McpError(ErrorCode.InvalidParams, "Missing required parameter: name")
                
                kind = arguments["kind"]
                name = arguments["name"]
                namespace = arguments.get("namespace")
                
                result = self.k8s_client.delete_resource(kind, name, namespace)
            
            elif tool_name == "get_resource_yaml":
                if "kind" not in arguments:
                    raise McpError(ErrorCode.InvalidParams, "Missing required parameter: kind")
                if "name" not in arguments:
                    raise McpError(ErrorCode.InvalidParams, "Missing required parameter: name")
                
                kind = arguments["kind"]
                name = arguments["name"]
                namespace = arguments.get("namespace")
                
                result = self.k8s_client.get_resource_yaml(kind, name, namespace)
            
            elif tool_name == "exec_command":
                if "pod_name" not in arguments:
                    raise McpError(ErrorCode.InvalidParams, "Missing required parameter: pod_name")
                if "command" not in arguments:
                    raise McpError(ErrorCode.InvalidParams, "Missing required parameter: command")
                
                pod_name = arguments["pod_name"]
                command = arguments["command"]
                namespace = arguments.get("namespace")
                container = arguments.get("container")
                
                result = self.k8s_client.exec_command(pod_name, command, namespace, container)
            
            else:
                raise McpError(ErrorCode.MethodNotFound, f"Unknown tool: {tool_name}")
            
            # Return the result
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
                    }
                ]
            }
        
        except McpError:
            # Re-raise MCP errors
            raise
        except Exception as e:
            logger.error(f"Error calling tool {request.params.name}: {str(e)}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def run(self):
        """Run the MCP server."""
        transport = StdioServerTransport()
        await self.server.connect(transport)
        logger.info("Kubernetes MCP server running on stdio")


def main():
    """Main entry point for the Kubernetes MCP server."""
    import asyncio
    
    # Create and run the server
    server = KubernetesMcpServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

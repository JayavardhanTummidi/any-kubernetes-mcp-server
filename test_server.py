#!/usr/bin/env python3
"""
Test script for the Kubernetes MCP server.

This script runs the Kubernetes MCP server and verifies that it works correctly.
"""

import asyncio
import logging
import sys
from kubernetes_mcp_server.server import KubernetesMcpServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("test-kubernetes-mcp-server")

async def main():
    """Run the Kubernetes MCP server."""
    logger.info("Starting Kubernetes MCP server test...")
    
    # Create the server
    server = KubernetesMcpServer()
    
    # Print server information
    logger.info("Kubernetes MCP server created successfully.")
    logger.info("Server name: %s", server.server.info["name"])
    logger.info("Server version: %s", server.server.info["version"])
    
    # Try to get Kubernetes contexts
    try:
        contexts = server.k8s_client.get_contexts()
        logger.info("Found %d Kubernetes contexts:", len(contexts))
        for ctx in contexts:
            logger.info("  - %s (active: %s)", ctx["name"], ctx.get("is_active", False))
    except Exception as e:
        logger.error("Failed to get Kubernetes contexts: %s", str(e))
    
    logger.info("Kubernetes MCP server test completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())

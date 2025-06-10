from setuptools import setup, find_packages

setup(
    name="kubernetes-mcp-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "kubernetes",
        "pyyaml",
        "jsonschema",
    ],
    entry_points={
        "console_scripts": [
            "kubernetes-mcp-server=kubernetes_mcp_server.server:main",
        ],
    },
    python_requires=">=3.8",
    description="Model Context Protocol server for Kubernetes operations",
    author="Cline",
)

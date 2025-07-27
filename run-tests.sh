#!/bin/bash

# Script to run molecule tests with different distributions
# Usage: ./run-tests.sh [distro]

set -e

# Default distribution
DEFAULT_DISTRO="debian12"
DISTRO="${1:-$DEFAULT_DISTRO}"

# Validate distribution parameter
case "$DISTRO" in
    debian11|debian12|ubuntu2004|ubuntu2404)
        echo "✓ Testing with distribution: $DISTRO"
        ;;
    *)
        echo "❌ Unsupported distribution: $DISTRO"
        echo "Supported distributions: debian11, debian12, ubuntu2004, ubuntu2404"
        exit 1
        ;;
esac

# Check if molecule is installed
if ! command -v molecule >/dev/null 2>&1; then
    echo "❌ Molecule is not installed. Installing..."
    pip install molecule[docker] molecule-plugins[docker]
fi

# Check if docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running or not accessible"
    exit 1
fi

# Set environment variables for molecule
export MOLECULE_DISTRO="$DISTRO"

# Determine docker command based on distribution
case "$DISTRO" in
    debian*)
        export MOLECULE_DOCKER_COMMAND="/lib/systemd/systemd"
        ;;
    ubuntu*)
        export MOLECULE_DOCKER_COMMAND="/lib/systemd/systemd"
        ;;
esac

echo "🧪 Running molecule tests..."
echo "📦 Distribution: $DISTRO"
echo "🐳 Docker command: ${MOLECULE_DOCKER_COMMAND:-default}"

# Clean up any existing molecule instances
molecule destroy || true

# Run the full molecule test suite
if molecule test; then
    echo "✅ Molecule tests completed successfully for $DISTRO"
    exit 0
else
    echo "❌ Molecule tests failed for $DISTRO"
    
    # Show logs for debugging
    echo "📋 Showing last container logs for debugging:"
    docker ps -a | grep molecule || true
    
    # Clean up
    molecule destroy || true
    exit 1
fi
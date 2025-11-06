#!/bin/bash
# Download script for SST container build sources
# Downloads MPICH, SST-core, and SST-elements source archives

set -e  # Exit on any error

# Default versions
DEFAULT_SST_VERSION="15.0.0"
DEFAULT_MPICH_VERSION="4.0.2"

# Parse command line arguments
SST_VERSION="${1:-$DEFAULT_SST_VERSION}"
MPICH_VERSION="${2:-$DEFAULT_MPICH_VERSION}"

# Validate SST version (check against known valid versions)
VALID_SST_VERSIONS=("14.0.0" "14.1.0" "15.0.0")
if [[ ! " ${VALID_SST_VERSIONS[@]} " =~ " ${SST_VERSION} " ]]; then
    echo "Warning: SST version ${SST_VERSION} may not be valid."
    echo "Known valid versions: ${VALID_SST_VERSIONS[*]}"
    echo "Continuing anyway..."
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [SST_VERSION] [MPICH_VERSION]"
    echo ""
    echo "Downloads source archives for SST container builds"
    echo ""
    echo "Arguments:"
    echo "  SST_VERSION    SST version to download (default: $DEFAULT_SST_VERSION)"
    echo "                 Valid versions: ${VALID_SST_VERSIONS[*]}"
    echo "  MPICH_VERSION  MPICH version to download (default: $DEFAULT_MPICH_VERSION)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Download defaults (SST $DEFAULT_SST_VERSION, MPICH $DEFAULT_MPICH_VERSION)"
    echo "  $0 15.0.0                    # Download SST 15.0.0, MPICH $DEFAULT_MPICH_VERSION"
    echo "  $0 15.0.0 4.1.1             # Download SST 15.0.0, MPICH 4.1.1"
    echo "  $0 --help                    # Show this help"
}

# Check for help flag
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_usage
    exit 0
fi

echo "=================================================="
echo "SST Container Source Download Script"
echo "=================================================="
echo "SST Version:   $SST_VERSION"
echo "MPICH Version: $MPICH_VERSION"
echo "=================================================="

# Download URLs
MPICH_URL="https://www.mpich.org/static/downloads/${MPICH_VERSION}/mpich-${MPICH_VERSION}.tar.gz"
SST_CORE_URL="https://github.com/sstsimulator/sst-core/releases/download/v${SST_VERSION}_Final/sstcore-${SST_VERSION}.tar.gz"
SST_ELEMENTS_URL="https://github.com/sstsimulator/sst-elements/releases/download/v${SST_VERSION}_Final/sstelements-${SST_VERSION}.tar.gz"

# Function to download with progress and error handling
download_file() {
    local url="$1"
    local filename="$2"
    local description="$3"

    echo ""
    echo "Downloading $description..."
    echo "URL: $url"
    echo "File: $filename"

    if [[ -f "$filename" ]]; then
        echo "File $filename already exists. Skipping download."
        echo "To re-download, delete the file first: rm $filename"
        return 0
    fi

    if wget --no-check-certificate --progress=bar:force "$url" -O "$filename"; then
        echo "✓ Successfully downloaded $filename"
        # Show file size
        echo "  File size: $(ls -lh "$filename" | awk '{print $5}')"
    else
        echo "✗ Failed to download $filename"
        echo "  URL: $url"
        rm -f "$filename"  # Remove partial download
        return 1
    fi
}

# Download MPICH
download_file "$MPICH_URL" "mpich-${MPICH_VERSION}.tar.gz" "MPICH ${MPICH_VERSION}"

# Download SST-core
download_file "$SST_CORE_URL" "sstcore-${SST_VERSION}.tar.gz" "SST-core ${SST_VERSION}"

# Download SST-elements
download_file "$SST_ELEMENTS_URL" "sstelements-${SST_VERSION}.tar.gz" "SST-elements ${SST_VERSION}"

echo ""
echo "=================================================="
echo "Download Summary"
echo "=================================================="

# Verify all files exist and show summary
files=(
    "mpich-${MPICH_VERSION}.tar.gz"
    "sstcore-${SST_VERSION}.tar.gz"
    "sstelements-${SST_VERSION}.tar.gz"
)

all_present=true
total_size=0

for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        size_bytes=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
        size_mb=$((size_bytes / 1024 / 1024))
        total_size=$((total_size + size_mb))
        echo "✓ $file (${size_mb} MB)"
    else
        echo "✗ $file (MISSING)"
        all_present=false
    fi
done

echo "=================================================="
echo "Total download size: ${total_size} MB"

if $all_present; then
    echo "✓ All files downloaded successfully!"
    echo ""
    echo "Files downloaded to current directory:"
    echo ""
    for file in "${files[@]}"; do
        echo "  $(pwd)/$file"
    done
    echo ""
    echo "Next steps:"
    echo "1. Files are ready in your current build directory"
    echo "2. Use the Containerfile to build an SST image"
else
    echo "✗ Some downloads failed. Check network connection and try again."
    exit 1
fi
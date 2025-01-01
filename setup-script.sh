#!/bin/bash

# Colors for prettier output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Scientific RAG Tool Setup${NC}"
echo "=============================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}Detected Python version:${NC} $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "\n${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "\n${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Function to check GPU availability
check_gpu() {
    if python3 -c "import torch; print(torch.cuda.is_available())" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Main installation function
install_dependencies() {
    local install_type=$1
    
    echo -e "\n${BLUE}Installing dependencies...${NC}"
    
    # Upgrade pip
    pip install --upgrade pip
    
    if [ "$install_type" == "dev" ]; then
        echo -e "${GREEN}Installing development dependencies...${NC}"
        pip install -r requirements-dev.txt
    else
        echo -e "${GREEN}Installing production dependencies...${NC}"
        pip install -r requirements.txt
    fi
    
    # Check if GPU is available and install appropriate torch version
    if check_gpu; then
        echo -e "\n${GREEN}GPU detected! Installing GPU-enabled PyTorch...${NC}"
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    else
        echo -e "\n${RED}No GPU detected. Installing CPU-only PyTorch...${NC}"
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    fi
}

# Present options to user
echo -e "\nPlease select installation type:"
echo "1) Production (minimal dependencies)"
echo "2) Development (includes testing and development tools)"
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        install_dependencies "prod"
        ;;
    2)
        install_dependencies "dev"
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "\n${BLUE}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Created .env file. Please update it with your configurations.${NC}"
fi

echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "To activate the virtual environment, run: ${BLUE}source venv/bin/activate${NC}"
echo -e "To start the development server, run: ${BLUE}uvicorn app.main:app --reload${NC}"
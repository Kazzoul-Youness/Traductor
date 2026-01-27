#!/bin/bash
# AllMuffins Translator Helper Script
# Quick commands for common tasks

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if venv exists
check_venv() {
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Virtual environment not found${NC}"
        echo -e "${YELLOW}Run: python3 -m venv venv${NC}"
        exit 1
    fi
}

# Activate venv
activate_venv() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
}

# Commands
case "$1" in
    setup)
        echo -e "${BLUE}🔧 Setting up environment...${NC}"
        python3 -m venv venv
        activate_venv
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Setup complete!${NC}"
        echo -e "${YELLOW}Next: Run './translate.sh test' to verify installation${NC}"
        ;;
    
    test)
        echo -e "${BLUE}🧪 Running tests...${NC}"
        check_venv
        activate_venv
        python test_quick.py
        ;;
    
    cost)
        echo -e "${BLUE}💰 Calculating costs...${NC}"
        check_venv
        activate_venv
        python cost_calculator.py
        ;;
    
    list)
        echo -e "${BLUE}📋 Listing recipes from sitemap...${NC}"
        check_venv
        activate_venv
        python recipe_translator.py list --limit ${2:-10}
        ;;
    
    translate)
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Missing URL${NC}"
            echo -e "${YELLOW}Usage: ./translate.sh translate <URL>${NC}"
            exit 1
        fi
        
        if [ -z "$CLAUDE_API_KEY" ]; then
            echo -e "${RED}❌ CLAUDE_API_KEY not set${NC}"
            echo -e "${YELLOW}Run: export CLAUDE_API_KEY='your-key-here'${NC}"
            exit 1
        fi
        
        echo -e "${BLUE}🌍 Translating: $2${NC}"
        check_venv
        activate_venv
        python recipe_translator.py translate "$2" \
            --langs ${3:-fr} \
            --api-key "$CLAUDE_API_KEY" \
            --save
        ;;
    
    batch)
        if [ -z "$CLAUDE_API_KEY" ]; then
            echo -e "${RED}❌ CLAUDE_API_KEY not set${NC}"
            echo -e "${YELLOW}Run: export CLAUDE_API_KEY='your-key-here'${NC}"
            exit 1
        fi
        
        COUNT=${2:-5}
        LANGS=${3:-fr}
        
        echo -e "${BLUE}🚀 Batch translating $COUNT recipes to $LANGS${NC}"
        check_venv
        activate_venv
        python recipe_translator.py batch \
            --count "$COUNT" \
            --langs $LANGS \
            --api-key "$CLAUDE_API_KEY"
        ;;
    
    clean)
        echo -e "${YELLOW}🧹 Cleaning up...${NC}"
        rm -rf translation_*.json
        rm -rf __pycache__ modules/__pycache__
        echo -e "${GREEN}✅ Cleaned${NC}"
        ;;
    
    help|*)
        echo -e "${BLUE}🧁 AllMuffins Translator Helper${NC}"
        echo ""
        echo "Usage: ./translate.sh <command> [options]"
        echo ""
        echo "Commands:"
        echo -e "  ${GREEN}setup${NC}              - Install dependencies"
        echo -e "  ${GREEN}test${NC}               - Run quick tests"
        echo -e "  ${GREEN}cost${NC}               - Calculate API costs"
        echo -e "  ${GREEN}list [N]${NC}           - List N recipes (default: 10)"
        echo -e "  ${GREEN}translate <URL>${NC}    - Translate one recipe"
        echo -e "  ${GREEN}batch [N] [LANG]${NC}  - Translate N recipes (default: 5, fr)"
        echo -e "  ${GREEN}clean${NC}              - Remove generated files"
        echo -e "  ${GREEN}help${NC}               - Show this help"
        echo ""
        echo "Examples:"
        echo "  ./translate.sh setup"
        echo "  ./translate.sh test"
        echo "  ./translate.sh list 20"
        echo "  export CLAUDE_API_KEY='sk-ant-...'"
        echo "  ./translate.sh translate 'https://allmuffins.com/chocolate-muffins'"
        echo "  ./translate.sh batch 10 'fr es'"
        echo ""
        ;;
esac

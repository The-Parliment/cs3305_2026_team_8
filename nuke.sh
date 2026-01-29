#!/bin/bash
echo "🔥 NUCLEAR CLEANUP - DESTROYING EVERYTHING..."

# Stop and remove
docker-compose down -v 2>/dev/null
docker stop $(docker ps -aq) 2>/dev/null
docker rm $(docker ps -aq) 2>/dev/null
docker rmi $(docker images -q) -f 2>/dev/null
docker volume rm $(docker volume ls -q) 2>/dev/null
docker network prune -f 2>/dev/null
docker system prune -af --volumes 2>/dev/null
docker builder prune -af 2>/dev/null

# Remove local database files
echo "🚀 Initializing Cleanup: Removing Docker-created databases with root privileges..."

sudo rm -rf dbdata/ 2>/dev/null
sudo rm -rf backend/auth/*.db 2>/dev/null
sudo rm -rf backend/auth/data/ 2>/dev/null
sudo rm -rf backend/*/test.db 2>/dev/null

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

echo "✅ Everything destroyed!"
echo ""
echo "Remaining containers:"
docker ps -a
echo ""
echo "Remaining images:"
docker images
echo ""
echo "Remaining volumes:"
docker volume ls
echo ""
echo "🚀 Ready for clean rebuild!"

# All tasks completed for this guide.

**Note:** This document reflects the development setup. It includes a reminder (TODO in `src/backend/main.py`) for configuring CORS properly for production, which is a crucial security step.

To enable your server-client setup, we need to modify a few things:

First, let's update the docker-compose.yml to bind to all interfaces instead of just localhost:
docker-compose.yml
Now, let's adjust the CORS configuration in FastAPI to accept connections from other machines:

main.py
To complete the server-client setup, here are the key points:

Server Setup (M2 Max):
The changes we just made allow the services to accept connections from any IP address
Your M2 Max needs to:
Have Docker and Docker Compose installed
Be accessible on your network (either local network or internet)
Have necessary ports open (8000, 3000, 3001, 9090)
Have a static IP or hostname for consistent access
Client Setup (Other Computers):
Development:
Use VSCode Remote SSH extension to connect to your M2 Max
Edit code directly on the M2 Max
Debug remotely
Usage:
Access the frontend via browser at http://[M2_MAX_IP]:3000
Access Grafana at http://[M2_MAX_IP]:3001
Access API docs at http://[M2_MAX_IP]:8000/docs
Security Considerations:
Currently set for development with allow_origins=["*"]
For production:
Use HTTPS
Restrict CORS to specific domains
Set up proper authentication
Use environment variables for sensitive configuration
Consider using a reverse proxy (like Nginx)

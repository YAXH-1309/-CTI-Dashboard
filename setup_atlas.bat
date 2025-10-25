@echo off
echo Setting up MongoDB Atlas (Cloud Database - Free Tier)
echo.

echo Step 1: Create MongoDB Atlas Account
echo Visit: https://www.mongodb.com/cloud/atlas/register
echo.

echo Step 2: Create a Free Cluster
echo - Choose "Shared" (Free tier)
echo - Select a cloud provider and region
echo - Cluster name: cti-dashboard
echo.

echo Step 3: Create Database User
echo - Go to Database Access
echo - Add New Database User
echo - Choose "Password" authentication
echo - Username: cti_user
echo - Generate a secure password
echo - Database User Privileges: "Read and write to any database"
echo.

echo Step 4: Configure Network Access
echo - Go to Network Access
echo - Add IP Address
echo - Choose "Allow access from anywhere" (0.0.0.0/0) for development
echo.

echo Step 5: Get Connection String
echo - Go to Clusters
echo - Click "Connect" on your cluster
echo - Choose "Connect your application"
echo - Copy the connection string
echo.

echo Step 6: Update .env file
echo Replace MONGODB_URI with your Atlas connection string:
echo MONGODB_URI=mongodb+srv://cti_user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/cti_dashboard?retryWrites=true^&w=majority
echo.

pause
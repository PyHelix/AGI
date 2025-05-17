# Deployment Guide

This document describes how to deploy `agiNet` securely on a server.

## Server Setup
1. Install BOINC server tools and Docker.
2. Copy the `server/` directory into your BOINC project.
3. Build the worker image:
   ```bash
   docker build -t aginet-worker .
   ```

## TLS Configuration
Use a reverse proxy such as Nginx to terminate TLS. Obtain certificates via
Let's Encrypt and ensure all worker communications use HTTPS.

## Firewall
Only expose ports required for BOINC and your reverse proxy. Block all other
inbound traffic using `ufw` or your cloud provider's firewall rules.

# ⚽ Premier League Standings Harvester (Cloud-Native Data Pipeline)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Azure](https://img.shields.io/badge/Microsoft_Azure-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)

## 📖 Project Overview
A fully automated, ephemeral data engineering pipeline that fetches live English Premier League (2023 Season) standings daily, processes the data, and securely loads it into a cloud SQL database for real-time visualization. 

This project demonstrates **Infrastructure as Code (IaC)**, **containerization**, and the **"Phoenix Server" architecture pattern**—meaning the entire infrastructure can be torn down and automatically rebuilt from scratch via CI/CD without human intervention.

## 🏗️ Architecture & Workflow
1. **GitHub Actions (CI/CD & Cron):** A workflow runs daily at 4:00 AM UTC.
2. **Infrastructure as Code (Bicep):** Automatically provisions an Azure Resource Group, Azure SQL Server, and manages networking/firewalls. Includes an automated "catch-all" script to safely purge soft-deleted Key Vaults during rebuilds.
3. **Ephemeral Compute (Azure Container Instances):** Pulls a custom Docker image from GitHub Container Registry (GHCR) containing the Python harvester script.
4. **Data Ingestion (Python & API-Sports):** The script dynamically securely retrieves the `FOOTBALL_API_KEY`, calls the API for the latest league standings, safely wipes yesterday's data (`TRUNCATE`), and inserts the fresh data to prevent duplicates.
5. **Visualization (Grafana):** A live Grafana dashboard queries the Azure SQL database to display a broadcast-quality Premier League table.

## 🛠️ Tech Stack
* **Language:** Python 3
* **Infrastructure as Code:** Azure Bicep
* **Cloud Provider:** Microsoft Azure (SQL Database, Container Instances)
* **Containerization:** Docker, GitHub Container Registry (GHCR)
* **Automation/CI-CD:** GitHub Actions
* **Visualization:** Grafana Cloud
* **Data Source:** API-Sports (Football API)

## ⚙️ Environment Variables & Secrets
To run this pipeline, the following secrets must be configured in GitHub Actions (`Settings > Secrets and variables > Actions`):

| Secret Name | Description |
| :--- | :--- |
| `DB_PASSWORD` | Secure password for the Azure SQL Database administrator. |
| `FOOTBALL_API_KEY` | Your unique API key from API-Sports. |
| `GH_REGISTRY_PASSWORD` | A GitHub Personal Access Token (PAT) with `write:packages` permissions to push the Docker image to GHCR. |

## 🚀 How It Works Under the Hood

### The Data Harvester (`harvester.py`)
The Python script is designed for idempotency. It connects to the Azure SQL database using `pyodbc`, ensures the `PremierLeagueStandings` table exists, and performs a complete data refresh:

`TRUNCATE TABLE PremierLeagueStandings;`

### The CI/CD Pipeline (`pipeline.yml`)
The GitHub Action is divided into two primary jobs:
1. **Build & Push:** Packages the Python script and dependencies into a Docker image and pushes it to GHCR.
2. **Deploy Infrastructure:** Uses Azure Bicep to deploy the SQL Database and executes `az container create` to spin up the ephemeral scraper with strict resource limits (`1 CPU`, `1.5 GB RAM`) and secure environment variables.

## 📊 Live Dashboard
The data is natively connected to Grafana using the Microsoft SQL Server plugin. The dashboard features custom value-mappings (e.g., dynamically coloring the 'Form' column green for Wins and red for Losses) to replicate professional sports analytics.
# ⚽ Premier League Standings Harvester (Cloud-Native Data Pipeline)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Azure](https://img.shields.io/badge/Microsoft_Azure-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

## 📖 Project Overview
A fully automated, ephemeral data engineering pipeline that fetches live English Premier League (2023 Season) standings daily, processes the data, and securely loads it into a cloud SQL database for real-time visualization. 

This project demonstrates **Infrastructure as Code (IaC)**, **containerization**, and the **"Phoenix Server" architecture pattern**—meaning the entire infrastructure can be torn down and automatically rebuilt from scratch via CI/CD without human intervention.

## 🏗️ Architecture & Workflow
1. **GitHub Actions (CI/CD & Cron):** A workflow runs every day @ 4am (For POC purposes).
2. **Infrastructure as Code (Bicep):** Automatically provisions an Azure Resource Group, Azure SQL Server, and manages networking/firewalls. Includes an automated "catch-all" script to safely purge soft-deleted Key Vaults during rebuilds.
3. **Ephemeral Compute (Azure Container Instances):** Pulls a custom Docker image from GitHub Container Registry (GHCR) containing the Python harvester script.
4. **Data Ingestion (Python & API-Sports):** The script securely retrieves the `FOOTBALL_API_KEY`, calls the API for the latest league standings, transforms the JSON into a Pandas DataFrame, and safely replaces yesterday's table (`if_exists="replace"`) to prevent duplicates.
5. **Visualization (Grafana):** A live Grafana dashboard queries the Azure SQL database to display a broadcast-quality Premier League table.

## 🛠️ Tech Stack
* **Language:** Python 3 (Pandas, SQLAlchemy, Requests)
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
The Python script is designed for complete idempotency. It transforms the raw API JSON into a clean Pandas DataFrame, then uses SQLAlchemy to connect to the Azure SQL Database. Instead of manually deleting old data, it leverages the Pandas `to_sql` method to safely drop and recreate the table on every run:

```python
# Drops the old table and creates a fresh one every time it runs to prevent duplicates
df.to_sql("PremierLeagueStandings", engine, if_exists="replace", index=False)
// --- PARAMETERS ---
param location string = resourceGroup().location
param sqlAdminUser string
@secure()
param sqlAdminPassword string
param myIpAddress string

// --- VARIABLES ---
var uniqueSuffix = uniqueString(resourceGroup().id)
var keyVaultName = 'kv-footy-${uniqueSuffix}' 
var sqlServerName = 'sqlserver-football-${uniqueSuffix}'

var resourceTags = {
  'football-stats-environment': 'dev'
}

// 1. THE VIRTUAL NETWORK
resource vnet 'Microsoft.Network/virtualNetworks@2023-04-01' = {
  name: 'vnet-football'
  location: location
  tags: resourceTags 
  properties: {
    addressSpace: {
      addressPrefixes: ['10.0.0.0/16']
    }
    subnets: [
      {
        name: 'snet-compute'
        properties: { addressPrefix: '10.0.0.0/24' }
      }
      {
        name: 'snet-db'
        properties: { addressPrefix: '10.0.1.0/24' }
      }
    ]
  }
}

// 2. THE KEY VAULT
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  tags: resourceTags 
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
  }
}

// 3. THE SQL SERVER
resource sqlServer 'Microsoft.Sql/servers@2022-05-01-preview' = {
  name: sqlServerName
  location: location
  tags: resourceTags 
  properties: {
    administratorLogin: sqlAdminUser
    administratorLoginPassword: sqlAdminPassword
  }
}

// 4. THE SERVERLESS SQL DATABASE
resource sqlDatabase 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {
  parent: sqlServer
  name: 'sqldb-football-stats'
  location: location
  sku: {
    name: 'GP_S_Gen5'
    tier: 'GeneralPurpose'
    family: 'Gen5'
    capacity: 1 
  }
}

// 5. THE SQL FIREWALL RULE 
resource sqlFirewall 'Microsoft.Sql/servers/firewallRules@2022-05-01-preview' = {
  parent: sqlServer
  name: 'AllowMyIP'
  properties: {
    startIpAddress: myIpAddress
    endIpAddress: myIpAddress
  }
}


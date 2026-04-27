#!/bin/sh
# Disable AutoConf
ipfs config --json AutoConf.Enabled false

# Replace 'auto' placeholders with empty arrays / explicit values
ipfs config --json Bootstrap '[]'
ipfs config --json DNS.Resolvers '{}'
ipfs config --json Routing.DelegatedRouters '[]'
ipfs config --json Ipns.DelegatedPublishers '[]'
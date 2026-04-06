#!/bin/sh

#pull test smart contracts container image
docker pull pramanan3/smartcontract_test:latest

#bring up the smart contract container
docker compose up test-smartcontracts -d

#clean previous data
docker compose up clean-data -d

#verify that qbft/QBFT-Network/Node2/data is empty

#make sure that the bootnode operator provides the genesis.json file to you
#on the bootnode, this file is located in qbft/QBFT-Network/networkFiles

#ensure that enode field is set to the bootnode1 enode address
#ensure that IP address is your own ip address.
#then launch node 2
docker compose up qbft-launch-node2

#add the bootnode enode explicitly
docker exec -it qbft-network-test-smartcontracts-1 bash -c "python add_peer.py 8546 enode://c4d889b6c7953e3e3348d187cc33f8d0ce3ea1ab87fa36b25e9eaa11db1feedd6e42947f519edbb8af57855fb7894e1889969ab7116a007138744ce8ac638dc4@10.227.82.47:30303"

#download abi.json, contract_address.json, compiled_code.json and run
docker exec -it qbft-network-test-smartcontracts-1 bash -c "python compile_SC_qbft.py 0 8546"
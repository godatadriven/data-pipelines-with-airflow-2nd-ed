#!/bin/bash

echo "========================================================="
echo "== Enable DNS to external containers in docker-compose =="
echo "========================================================="
PATCH_FILE=$(mktemp /tmp/core-dns.patch.XXXXXX)

echo "===================================================="
echo "== Determine nodehosts and write to ${PATCH_FILE} =="
echo "===================================================="
echo -e "data:\n  NodeHosts: |\n$(echo -e "$(for host in postgres; do echo -n "$(nslookup -type=a $host | grep Address | awk -F':' '{gsub(/ /, "", $2);printf("%4s%s\n", " ", $2)}' | tail -n1) $host\n"; done)$(kubectl -n kube-system get configmap coredns -o go-template='{{ .data.NodeHosts }}' | awk '{ printf("%4s%s\n", " ", $0)}')" | sort -u)" > ${PATCH_FILE}

echo "=========================================="
echo "== Patch coredns NodeHosts in configmap =="
echo "=========================================="
kubectl -n kube-system patch cm coredns --patch-file ${PATCH_FILE}

echo "====================="
echo "== Restart coredns =="
echo "====================="
kubectl --wait=false -n kube-system delete pod -l k8s-app=kube-dns

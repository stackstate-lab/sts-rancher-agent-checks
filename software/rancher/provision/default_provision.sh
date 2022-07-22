#!/bin/bash

 apt-get update -y
# Install Docker
# Reference: https://docs.docker.com/engine/install/ubuntu/
apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common dnsmasq resolvconf

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
apt-key fingerprint 0EBFCD88
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io network-manager

# Add vagrant user to docker group (Running docker command without sudo)
addgroup -a vagrant docker
chmod 666 /var/run/docker.sock

apt-get install -y zsh build-essential file git unzip

echo "interface=docker0" >> /etc/dnsmasq.conf
echo "bind-interfaces" >> /etc/dnsmasq.conf
echo "listen-address=172.17.0.1" >> /etc/dnsmasq.conf
echo "nameserver 172.17.0.1" >> /etc/resolvconf/resolv.conf.d/tail

cat <<EOT >> /etc/docker/daemon.json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOT


service network-manager restart
resolvconf -u
service dnsmasq restart
service docker restart

# install rancher
docker run -d --restart=unless-stopped -p 8080:8080 --name rancher-server rancher/server:stable

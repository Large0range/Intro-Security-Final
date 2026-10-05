sudo ip netns add hostA
sudo ip netns add hostB
sudo ip link add vethA type veth peer name vethB
sudo ip link set vethA netns hostA
sudo ip link set vethB netns hostB
sudo ip netns exec hostA ip addr add 10.0.0.1/24 dev vethA
sudo ip netns exec hostB ip addr add 10.0.0.2/24 dev vethB
sudo ip netns exec hostA ip link set vethA up
sudo ip netns exec hostB ip link set vethB up
sudo ip netns exec hostA ip link set lo up
sudo ip netns exec hostB ip link set lo up

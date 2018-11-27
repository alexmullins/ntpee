$provision_script = <<-SCRIPT
echo "I am provisioning..."
sudo bash -c 'echo "192.168.30.2  vm1 vm1" >> /etc/hosts'
sudo bash -c 'echo "192.168.30.3  vm2 vm2" >> /etc/hosts'
sudo bash -c 'echo "192.168.30.4  vm3 vm3" >> /etc/hosts'
SCRIPT

Vagrant.configure("2") do |config|
    # set the linux vm box
    config.vm.box = "ubuntu/bionic64"
    config.vm.provider "virtualbox" do |v|
        v.linked_clone = true
    end
    $num_boxes = 3
    # loop $num_boxes times
    (1..$num_boxes).each do |i|
        # define new vm config
        config.vm.define "vm#{i}" do |node|
            # set hostname
            node.vm.hostname = "vm#{i}"
            # set provision script
            node.vm.provision "shell", inline: $provision_script, privileged: false
            # set ip address
            node.vm.network "private_network", ip: "192.168.30.#{i+1}"
        end
    end
end

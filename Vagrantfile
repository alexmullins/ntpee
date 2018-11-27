$provision_script = <<-SCRIPT
echo "I am provisioning..."
sudo apt-get update
sudo apt-get install -y openbsd-inetd finger fingerd

sudo bash -c 'echo "echo stream tcp nowait root internal" >> /etc/inetd.conf'
sudo bash -c 'echo "finger stream tcp nowait nobody /usr/sbin/tcpd in.fingerd -f" >> /etc/inetd.conf'
sudo /etc/init.d/openbsd-inetd restart

sudo bash -c 'echo "192.168.30.2  vm1 vm1" >> /etc/hosts'
sudo bash -c 'echo "192.168.30.3  vm2 vm2" >> /etc/hosts'
sudo bash -c 'echo "192.168.30.4  vm3 vm3" >> /etc/hosts'
SCRIPT

$rustup_script = <<-SCRIPT
curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain nightly
SCRIPT

Vagrant.configure("2") do |config|
    # set the linux vm box
    config.vm.box = "ubuntu/trusty64"
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
            if i == 1 then
                node.vm.provision "shell", inline: $provision_script + $rustup_script, privileged: false
            else
                node.vm.provision "shell", inline: $provision_script, privileged: false
            end
            # set ip address
            node.vm.network "private_network", ip: "192.168.30.#{i+1}"
        end
    end
end
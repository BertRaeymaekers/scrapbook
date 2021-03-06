Vagrant.configure("2") do |config|

  # Virtualbox
  config.vm.box = "debian/stretch64"
  config.vm.hostname = 'dr0-vb'
  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = false
    # Customize the amount of memory on the VM:
    vb.memory = "512"
  end

  ## Using my ssh key.
  #config.ssh.private_key_path = "~/.ssh/id_rsa"
  config.ssh.guest_port = "2200"

  # Adding my key in the VM.
  config.vm.provision "shell" do |s|
    ssh_pub_key = File.readlines("#{Dir.home}/.ssh/id_rsa.pub").first.strip
    s.inline = <<-SHELL
      echo #{ssh_pub_key} >> /home/vagrant/.ssh/authorized_keys
    SHELL
  end

  # Using Ansible
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "playbook.yml"
    ansible.group = {
      "susm-api" => ["d0", "d0-vb"],
      "DEV" => ["d0-vb"],
      "PRO" => ["d0"]
    }
  end

  # Port forwarding
  config.vm.network :forwarded_port, guest: 80, host: 8000

end

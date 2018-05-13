Vagrant.configure("2") do |config|

  # Virtualbox
  config.vm.box = "debian/stretch64"
  config.vm.hostname = 'dr0'
  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = false
    # Customize the amount of memory on the VM:
    vb.memory = "512"
  end

  ## Using my ssh key.
  #config.ssh.private_key_path = "~/.ssh/id_rsa"

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
  end

  # Port forwarding
  config.vm.network :forwarded_port, guest: 22, host: 2200
  config.vm.network :forwarded_port, guest: 80, host: 8000

end

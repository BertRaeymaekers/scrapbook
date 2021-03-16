certificates/create
===================

Create certificate: create private key/certificate signing request (csr).

Requirements
------------

This role uses openssl.

Role Variables
--------------

Required variables:

- `certificate_name`: Name of the certificate, with path. The private key file created will ".key" attached, the certificate signing request will have ".crs" attached.
- `certificate_CN`: Common Name (CN) to use in the certificate. This is usually the URL or FQDN of the server.
- `state`: Any of the folowing four options. In most cases you need "csr".
  - *key*: Check if there is a private key, and if not create it.
  - *rekey*: Create the private key (potentially overwriting an existing one).
  - *csr*: Check both for a private key and a csr, and if needed create them.
  - *recsr*: Generate a csr for the private key (potentially overwriting an existing one). It will create the private key if not present.

Optional variable:

- `certificate_passphrase`: Use this if you want to protect your private key with a passphrase. Hint: use a vault.
- `certificate_key_size`: Key size used to generate certificates. Defaults to 4096.
- `certificate_O`: Organization to be set on the certificate. Defaults to FOOBAR.

Internal variable you normally don't need to touch:

Dependencies
------------

None.

Example Playbook
----------------

Simple example:

```yaml
- name: Create a private key and csr
  hosts: localhost
  tasks:
    - name: Create a private key and csr
      import_role:
        name: certificates/create
      vars:
        certificate_name: "/tmp/example"
        certificate_CN: "www.example.com"
```

Example using certificate/create and certificate/ca.

```yaml
- name: "Test the use of a private certificate authority and certificate creation"
  hosts: host1, host2, host3
  
  tasks:

    - set_fact:
        cert_name: "{{ ansible_host }}"
        CN: "{{ ansible_host }}.local"
  
    - debug:
        msg: "Certificate name: {{ cert_name }}"
    - debug:
        msg: "Certificate name: {{ cert_name }}"
      delegate_to: host0

    - name: Create CSR
      include_role:
        name: certificates/create
      vars:
        state: csr
        certificate_name: "/tmp/{{ cert_name }}"
        certificate_CN: "{{ CN }}"

    - name: TODO COPY

    - name: Sign CSR
      include_role:
        name: certificates/authority
        apply:
          delegate_to: host0
      vars:
        certificate_authority_path: "/tmp/test-ca"
        certificate_authority_passphrase: "myverysecretpassphrase"
        # Almost 30 years.
        validity_period: 10950
        certificate_csr: "{{ cert_name }}.csr"
        certificate_CN: "{{ CN }}"

    - name: TODO COPY
        
    # TODO: check if private kay and public key match.
    # WISHLIST: a p12 role for key+cer => p12 or p12 > key+cer
```

License
-------

BSD

Author Information
------------------

Bert Raeymaekers <ansilbe.role.certificates@schldl.com>

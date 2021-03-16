certificates/authority
======================

Manage your own very simple certificate authority (CA).

**NOTE**: We do not check if the CA is still valid at this time (the role might go in error after expiration, I don't know).

Requirements
------------

This role uses openssl.

Role Variables
--------------

Required variables for creating a CA:

- `certificate_authority_passphrase`: passphrase to the CA private key. **Hint**: Use a vault.

Extra required variables for signing a certificate signing request (csr):

- `certificate_csr`: full path to the .csr file to sign.

Properties for the CA itself:

- `certificate_authority_path`: Path to use for the CA. Defaults to certificate-authority under the home directory.
- `certificate_authority_validity_period`: Validity period for the CA in days. Defaults to 10950 days (~30 years).
- `certificate_authority_CN`: Common Name (CN) for the CA. Defaults to the hostname (without "a-" if present).
- `certificate_authority_O`: Organization for the CA. Defaults to "FOOBAR"
- `certificate_key_size`: CA certificate key size. Defaults to 4096.

Properties for csr to sign:

- `certificate_validity_period`: Validity period for the certificate in days. Defaults to 10950 days (~30 years).
- `certificate_crt`: Signed certificate file. Defaults to certificate_csr but with the .cer extension.
- `certificate_ext`: Extension file for a csr file. Defaults to certificate_csr but with the .ext extension.
- `certificate_ALT`: List of alternative names. Defaults to a list just containing the certificate CN.

Dependencies
------------

TODO

Example Playbook
----------------

Example using certificate/create and certificate/ca where the CA is on host0 and certifictes are created for host1, host2 and host3.

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

    - name: TODO copy

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

    - name: TODO copy
```

License
-------

BSD

Author Information
------------------

Bert Raeymaekers <ansible.role.certificates@schldl.com>

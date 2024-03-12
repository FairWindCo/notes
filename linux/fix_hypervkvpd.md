Маэмо в лозі наступну помилку:
`more /var/log/syslog | grep "hv_get_dhcp_info: not found"`

`hv_kvp_daemon[5073]: sh: 1: /usr/libexec/hypervkvpd/hv_get_dhcp_info: not found`
Виправлення це створити необхідні посилання
```
mkdir /usr/libexec/hypervkvpd
ln -s /usr/sbin/hv_get_dhcp_info /usr/libexec/hypervkvpd/hv_get_dhcp_info
ln -s /usr/sbin/hv_get_dns_info /usr/libexec/hypervkvpd/hv_get_dns_info
```

[https://askubuntu.com/questions/1109982/e-could-not-get-lock-var-lib-dpkg-lock-frontend-open-11-resource-temporari]

Або ось такий фрагмент з сценарію ансібл:

```
---
# tasks file for fix_hv_kvp
  - name:  check errors in syslog
    ansible.builtin.shell:
      cmd: more /var/log/syslog | grep 'hv_get_dhcp_info'
    become: true
    register: log_state

  - block:
    - name: create directory
      ansible.builtin.file:
        path: /usr/libexec/hypervkvpd
        state: directory
        mode: '0755'
        owner: root
        group: root

    - name: soft link hv_get_dhcp_info
      ansible.builtin.file:
        owner: root
        group: root
        src: /usr/sbin/hv_get_dhcp_info
        dest: /usr/libexec/hypervkvpd/hv_get_dhcp_info
        state: link

    - name: soft link hv_get_dns_info
      ansible.builtin.file:
        owner: root
        group: root
        src: /usr/sbin/hv_get_dns_info
        dest: /usr/libexec/hypervkvpd/hv_get_dns_info
        state: link

    become: true
    when: log_state.stdout

```

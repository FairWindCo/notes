# На системах microsoft vmm
В варіанті з динамічною паміттю, маємо проблему, яка полягіє в тому, що кубернетіс не бачить пам'ять яку виділяє віртуалізтор після страту демона кубера. Потрібно розкачати пам'ять до почтаку роботи кубера, щоб він міг бачити модливість виділення пам'яті.

## Встановити пакет
`apt install stress`

## Відредагувати файл:
/etc/systemd/system/kubelet.service.d/10-kubeadm.conf
Повинен мати такий фигляд:
```
# Note: This dropin only works with kubeadm and kubelet v1.11+
[Service]
Environment="KUBELET_KUBECONFIG_ARGS=--bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf --kubeconfig=/etc/kubernetes/kubelet.conf"
Environment="KUBELET_CONFIG_ARGS=--config=/var/lib/kubelet/config.yaml"
# This is a file that "kubeadm init" and "kubeadm join" generates at runtime, populating the KUBELET_KUBEADM_ARGS variable dynamically
EnvironmentFile=-/var/lib/kubelet/kubeadm-flags.env
# This is a file that the user can use for overrides of the kubelet args as a last resort. Preferably, the user should use
# the .NodeRegistration.KubeletExtraArgs object in the configuration files instead. KUBELET_EXTRA_ARGS should be sourced from this file.
EnvironmentFile=-/etc/default/kubelet
ExecStart=
ExecStart=/usr/bin/kubelet $KUBELET_KUBECONFIG_ARGS $KUBELET_CONFIG_ARGS $KUBELET_KUBEADM_ARGS $KUBELET_EXTRA_ARGS
ExecStartPre=/usr/bin/stress -m 15 -t 30 --vm-bytes 512m
StartLimitInterval=360
StartLimitBurst=30
```
Фактично додано наступні строки:
```
ExecStartPre=/usr/bin/stress -m 15 -t 30 --vm-bytes 512m
StartLimitInterval=360
StartLimitBurst=30
```

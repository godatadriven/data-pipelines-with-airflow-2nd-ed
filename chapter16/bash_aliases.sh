alias kubectl='kubectl -s https://k3s-server:6443 "${@}"'
alias helm='helm --kube-apiserver https://k3s-server:6443 "${@}"'

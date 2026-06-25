# Firecracker integration

## What changed

The project now has two execution backends:

- `subprocess` — portable development/test backend and the default.
- `firecracker` — Linux/KVM backend that starts one disposable Firecracker microVM per invocation.

The selection is made with:

```bash
OBLAK_EXECUTION_BACKEND=subprocess
# or
OBLAK_EXECUTION_BACKEND=firecracker
```

The service no longer imports the subprocess orchestrator directly. It calls `create_orchestrator()` from `oblak/orchestrator/factory.py`, which returns the configured backend.

## Important files

- `oblak/orchestrator/factory.py` — chooses the execution backend.
- `oblak/orchestrator/firecracker.py` — host-side Firecracker orchestration.
- `firecracker/rootfs_overlay/sbin/oblak-init` — guest-side init process that runs the uploaded `handler.py`.
- `scripts/build_firecracker_rootfs.sh` — helper for copying `oblak-init` into a Linux rootfs image.
- `oblak/core/config.py` — Firecracker-related settings.
- `oblak/services/function_service.py` — uses the orchestrator factory when invoking functions.

## Required host setup

The Firecracker backend must run on Linux with KVM:

```bash
test -e /dev/kvm
firecracker --version
which mkfs.ext4
which debugfs
```

You also need:

1. Firecracker binary, usually `/usr/local/bin/firecracker`.
2. A Linux kernel image, for example `./firecracker/vmlinux`.
3. A prepared root filesystem image, for example `./firecracker/rootfs.ext4`.

Example environment:

```bash
export OBLAK_EXECUTION_BACKEND=firecracker
export OBLAK_FIRECRACKER_BINARY=/usr/local/bin/firecracker
export OBLAK_FIRECRACKER_KERNEL_IMAGE=./firecracker/vmlinux
export OBLAK_FIRECRACKER_ROOTFS_IMAGE=./firecracker/rootfs.ext4
export OBLAK_FIRECRACKER_VCPU_COUNT=1
export OBLAK_FIRECRACKER_MEM_SIZE_MIB=256
export OBLAK_EXECUTION_TIMEOUT_SECONDS=5
```

## Execution pipeline with Firecracker

1. The user uploads a zip through the CDK CLI.
2. `FunctionService.upload()` validates, stores, extracts, verifies and prepares the function.
3. If `requirements.txt` exists, dependencies are installed into the function-local `.oblak-deps` directory.
4. On invocation, `FunctionService.invoke()` calls the configured orchestrator.
5. `FirecrackerOrchestrator` creates a disposable ext4 image containing only the prepared function directory.
6. Firecracker starts a fresh microVM with:
   - one kernel image,
   - one rootfs image,
   - one read-only code drive,
   - configured vCPU and memory limits,
   - no host directory mount.
7. The guest `/sbin/oblak-init` mounts the read-only code drive, loads `handler.py`, executes `handler(event, context)`, prints `__OBLAK_RESULT__...` to the serial console and powers off.
8. The host parses the serial console output and stores the invocation result.

## Security explanation for defence

The key security point is that the uploaded code is not executed inside the API server process. With the Firecracker backend it runs inside a separate microVM. The microVM receives only a read-only ext4 image containing the prepared function. It does not receive the host storage directory, the project root, the database file, the `.env` file or arbitrary host paths.

The subprocess backend is still present only so the project remains runnable on machines without Linux/KVM. It is not equivalent to Firecracker isolation.

## About `pip install`

In this project, `pip install` still happens during the preparation phase in `FunctionService._prepare()`. Dependencies are installed with `pip --target <function>/.oblak-deps`, not into the server environment.

For a production system, this should be moved to a disposable builder worker or builder microVM, with queueing, rate limiting and dependency caching. The current project already has partial DoS controls: max archive size, max requirements lines and dependency installation timeout.

## Firecracker configuration points

The host-side configuration is performed through Firecracker's API socket:

- `/logger` — log path and log level.
- `/metrics` — metrics path.
- `/boot-source` — kernel image and boot args.
- `/drives/rootfs` — guest root filesystem.
- `/drives/code` — read-only per-invocation code image.
- `/machine-config` — vCPU count, memory size and SMT disabled.
- `/vm` — changes VM state to `Resumed`.

## Jailer note

For stricter production isolation, start Firecracker through `jailer` and run it under a dedicated unprivileged user, with a per-VM chroot directory. The code is structured so the Firecracker API configuration remains the same after the jailed process creates the API socket.

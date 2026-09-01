# Package projects

Each directory is a self-contained Apple Pkl package project with its own `PklProject` and semantic version.

Current packages:

- `openbim.loin/`: ISO 7817-3 / EN 17412-3 Level of Information Need contracts.

Do not make one package depend on another through relative source imports. Published cross-package relationships use `Project.RemoteDependency` and are locked in `PklProject.deps.json`.

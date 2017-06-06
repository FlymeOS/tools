[English](./CHANGELOG.md) | 简体中文


#### Flyme 6.7.5.15 (2017-05-16)

- 【新增】支持在 `sepolicy` 中注入新的权限规则。根据机型的需要，可以在机型目录使用 `custom_sepolicy` 脚本自行定制需要注入的权限规则。根据机型的需要，可以在 `Makefile` 文件中自行配置是否注入 `sepolicy` 新的权限规则。


#### Flyme 6.7.5.8 (2017-05-09)

- 【修复】某些情况下合并 odex 时出错的问题。
- 【修复】修复 `autopatch` 时没有备份 `smali_classes2` 文件夹到 `autopatch` 文件夹的问题（感谢 `wuxianlin` 的反馈）。


#### Flyme 6.7.5.2 (2017-05-02)

- 初始发布。
- 【新增】支持 `Android Marshmallow`（6.0.1）。
- 【新增】适配 Flyme 6。

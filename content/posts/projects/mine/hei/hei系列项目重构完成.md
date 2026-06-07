---
title: "Hei 系列项目重构完成：两个月磨一剑，四项目同步升级"
date: 2026-06-07
draft: false
description: 耗时两个月，借助 DeepSeek + Codex + Claude Code 完成了 hei-admin-vue、hei-gin、hei-fastapi、hei-pc-vue 四个项目的深度重构与完善，涵盖插件化架构、双端认证、RBAC 权限、WebSocket IM、国密加密等核心能力
categories:
  - 开源项目
tags:
  - Hei
  - Vue
  - Go
  - Python
  - FastAPI
  - Gin
  - AI
  - Codex
  - DeepSeek
  - Claude Code
---

过去两个月，我集中精力把 **Hei 系列** 四个核心项目翻了个底朝天。这篇文章记录一下做了什么、踩了什么坑、以及最后的成果。

如果你还不太了解 Hei——它是一整套前后端分离的快速开发框架，名字来自国漫《罗小黑战记》里那只小黑猫。Logo 是个猫头，开源协议 MIT，免费可商用。

## 项目全景

四个项目，各司其职：

| 项目 | 技术栈 | 角色 |
|------|--------|------|
| **Hei Gin** | Go + Gin + GORM | B 端后端，主框架 |
| **Hei FastAPI** | Python + FastAPI + SQLAlchemy | B 端后端，姊妹框架 |
| **Hei Admin Vue** | Vue 3 + Ant Design Vue | B 端管理后台 |
| **Hei PC Vue** | Vue 3 + Ant Design Vue | C 端门户前台 |

打通了完整的前后端分离架构，业务功能保持一致，可以根据口味选 Go 还是 Python 做后端。

## 两个月干了什么

翻了一下 git log，按时间线把这两个月的活捋一捋。

### 第一阶段：搭骨架（四月中到五月中）

这阶段主要是在 Hei Gin 这边搭插件化架构的架子。

```
2026-05-16  rebuild     ← 推了重写
2026-05-16  bad         ← 写砸了
2026-05-16  rebase      ← 救一下
2026-05-16  rebase      ← 再救一下
2026-05-15  init        ← 重来吧
2026-05-15  init        ← 认真的
2026-05-15  init        ← 这次真的
2026-05-15  end         ← 我放弃了（缓一下）
```

那段时间确实不太顺利。插件化架构说起来简单——模块自注册、自动发现路由和权限——但真要拆得干净、扩展起来不别扭，来回试了好几版。中间一度想算了，直接"推到重写"然后又"写砸了"，反复了好几次。

还有一个大决定：从 Ent 迁移到 GORM。

```
2026-05-27  迁移到gorm
2026-05-27  迁移到gorm
2026-05-27  修复问题
2026-05-27  优化迁移
```

之前用 Ent，代码生成确实爽，但维护起来心智负担重——改个表结构要重新 generate，多人协作时 schema 文件容易打架。GORM 虽然啰嗦一点，但胜在简单直接，不用养一个代码生成步骤。对于个人项目来说，少一层是一层。

同期还做了个大决定：把 JWT 换成随机 Token。

```
2026-05-31  feat: 将JWT认证替换为Token认证并集成GORM ORM
2026-05-31  refactor(ent): 移除Ent框架相关代码和依赖
```

JWT 的好处是无状态、不用查库，但坏处是没法主动下线——踢人、改权限要等 token 过期。换成 Redis 存 Token 后，在线会话管理、强制下线、多端互踢都自然支持了。为了这个改动，前端也做了配套升级：

```
2026-05-14  feat(auth/session): add token management for user sessions
```

### 第二阶段：加功能（五月中到五月底）

架构稳住之后开始往上堆功能。

**IM 系统**是这轮重头戏。git log 里这一段的密度明显上来了：

```
Hei Gin:
2026-06-03  feat: 添加消息模块和WebSocket支持
2026-06-04  站内信
2026-06-04  架构更新
2026-06-04  feat(plugin-im): 添加群聊功能并扩展消息系统
2026-06-06  feat(plugin-im): 添加文件上传功能并优化消息系统

Hei FastAPI:
2026-05-31  feat(auth): 将JWT认证替换为随机Token认证
2026-06-07  feat(plugin_im): 添加消息分页、详情和删除功能
2026-06-07  perf(plugin_im): 优化好友列表和群组成员查询性能

Hei Admin Vue:
2026-06-03  feat: 添加WebSocket消息通知功能
2026-06-04  站内信
2026-06-04  feat(MessageBell): 添加下拉菜单状态监听
2026-06-06  feat(im): 添加好友屏蔽和备注功能

Hei PC Vue:
2026-05-??  站内信
2026-05-??  feat(im): 添加IM聊天功能和群组管理系统
```

IM 跨实例的设计用了 Redis List + BRPOP——每个实例一个消息队列，用阻塞读去拉。不引入消息队列中间件，Redis 就能搞定。

**权限模型**也重构了。之前权限和数据范围绑在一起，扩展起来别扭。改成了每个权限独立配置数据范围：

```
Hei Gin:
2026-06-01  feat(auth): 添加超级管理员权限绕过机制

Hei FastAPI:
2026-05-??  refactor(permission): 同权限多路径时按维度独立合并数据范围

Hei Admin Vue:
2026-05-??  feat: redesign permission model — per-permission data scope
```

**限流和防重复提交**也安排上了：

```
2026-06-06  feat(middleware): 添加API限流中间件功能
```

### 第三阶段：基本可用的 MVP 版本（六月第一周）

最后一周基本在打磨文档、修细节、补充工具链。

Hei Gin 这边：

```
2026-06-07  feat(codegen): 添加插件代码生成工具支持
2026-06-07  docs(README): 更新框架介绍描述  （×N 条）
```

Hei Admin Vue 的 IM 模块迭代得很快：

```
2026-06-06  refactor(im): 优化API接口类型定义
2026-06-06  feat(im): 消息中心重构为对话和通知两个标签页
2026-06-06  feat(im): 添加通知功能
2026-06-06  feat(im): 添加群组为空时的提示信息
```

**codegen 工具**是最后几天加的——写插件的时候频繁重复"建目录、写模板文件、注册路由"这套流程，干脆搓了个脚手架生成器，一条命令生成插件骨架。

## 重构要点速览

### 1. 插件化架构

两个后端最大的重构。每个业务模块以插件形式自注册：

- **Hei Gin** 通过 `module.Register()` 管理 Init / Start / Stop 生命周期，自动发现路由、权限、中间件、定时任务、DB 模型和种子数据
- **Hei FastAPI** 采用 `HeiPlugin` 子类 + 装饰器模式，`Perm("code", "name")` 一句同时完成权限注册和运行时校验

加新模块只需往 `plugins/` 丢一个包，启动自动接入，零配置。

### 2. 双端认证体系

B 端和 C 端各一套独立 Token 认证，API 路径前缀自动分流。支持：

- Token 签发/刷新/销毁
- 在线会话管理（查看在线用户 + 强制下线）
- SM2 国密加密传输登录密码
- bcrypt 加盐哈希存储密码
- SM3 签名防篡改操作日志

### 3. RBAC 权限 + 行级数据权限

三层结构：用户 → 角色 → 权限，支持用户直授。数据范围支持 8 种粒度，多角色按最严策略合并。

### 4. 跨实例 WebSocket IM

Redis List + BRPOP 驱动，不依赖消息队列中间件：

- 用户连接追踪（Redis Set）
- 实例独享消息队列（Redis List）
- SETNX 消息去重 + 滑动窗口限流
- 心跳检测 + 僵尸实例清理
- 好友聊天 + 群聊

### 5. 抽象文件存储

统一接口，三种后端配置切换：Local / MinIO / S3。支持分片上传。

### 6. 前端同步升级

Vite 8.x + TypeScript 5.x/6.x + UnoCSS + Sass + Alova 3.x + Pinia。

**Admin** 覆盖：仪表盘、用户/角色/资源/部门管理、字典、系统配置、公告、横幅、文件、日志、在线用户、个人中心。

**PC Vue** 覆盖：首页、关于、公告、C 端登录注册、个人中心、IM、文件上传。页面默认公开访问。

### 7. 工具链

- 数据库迁移 CLI：自动发现 Model，一键迁移 + 种子数据
- 插件代码生成器：快速生成插件骨架
- VitePress 文档站：四个项目各有独立在线文档

## 为什么用 AI

这两个月 DeepSeek + Codex + Claude Code 是主力干活工具。

AI 帮我搞定的：

- **跨项目批量改写**：Go 和 Python 两套后端要功能对等，逐文件改是纯体力活，Codex 批量 patch 一把梭
- **架构讨论**：插件化设计的 edge case、WebSocket 跨实例选型、权限匹配器通配符规则——DeepSeek 的 reasoning 讨论方案确实好用
- **文档补全**：CLI 说明、配置项、API 规范这类高频但容易忽略的内容，Claude Code 生成一次成型
- **迁移脚本**：从旧结构迁到插件化新结构，路由注册、中间件挂载、配置加载的批量修改

AI 搞不定的：

- **架构决策**：要不要从 Ent 迁 GORM、JWT 换 Token、权限模型怎么拆——这些得自己拿主意
- **测试验证**：改完了跑不跑得通，还是得自己点一遍
- **模块拆分边界**：哪些功能应该放一起、哪些应该拆开，AI 对项目整体感的判断还差点意思

说白了，AI 把"做苦工"的成本降到了可以接受的程度，让一个人能在两个月里同时翻修四个项目。但钥匙在谁手里、车往哪开，还是得自己决定。

## 关于 Hei

名字来自《罗小黑战记》，logo 是个猫头。这系列最开始就是为自己做的——我需要一套趁手的脚手架来快速搭项目。

其实我的主力语言是 Java，之前也做过 Hei Boot（Spring Boot 版）和 Hei Cloud（Spring Cloud 微服务版）。那为什么这次重构先选了 Go 和 Python？

一是**工作也在用**。虽然主力是 Java，但日常工作中 Go 和 Python 也占了不小的比例，尤其是写工具、做脚本、搭小服务的时候，Go 和 Python 反而上手更快。

二是**成本低**。Go 编译完一个二进制就能跑，Python 有环境就能跑，开发迭代的摩擦小很多。Java 那套——Maven/Gradle 构建、JVM 参数调优、Spring 全家桶的启动时间——对于个人脚手架来说有点重了。

三是**AI Agent 生态**。这两年的 AI 编码工具，对 Python 和 Go 的支持是最好的。Python 本身就是 AI 的第一语言；Go 简洁、静态、类型明确，AI 生成代码的准确率也高。Java 相对偏企业级、偏传统，Agent 生成的质量和效率明显差一截。

技术栈选的都是我用得顺手的：Go 写后端清爽，Python 写脚本快，Vue 写前端不别扭。

如果你觉得有用，欢迎 Star 或 Fork；如果发现问题或有好想法，欢迎提 Issue 或 PR。

## 后续计划

- **Hei Boot**（Java Spring Boot）规划中
- **Hei Cloud**（Spring Cloud 微服务版）规划中
- **Hei Uniapp**（UniApp + Vue3 跨平台移动端）规划中
- **Hei Flutter**（Flutter 跨平台移动端）规划中
- 测试覆盖率提升
- 更好的错误提示和异常处理

## 项目地址

- [Hei Gin](https://github.com/jiangbyte/hei-gin) — Go 后端
- [Hei FastAPI](https://github.com/jiangbyte/hei-fastapi) — Python 后端
- [Hei Admin Vue](https://github.com/jiangbyte/hei-admin-vue) — 管理后台
- [Hei PC Vue](https://github.com/jiangbyte/hei-pc-vue) — C 端门户
- [Hei Uniapp](https://github.com/jiangbyte/hei-uniapp) — UniApp 跨平台移动端

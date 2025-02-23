# Todo 管理助手

一个友好的 Telegram 机器人，帮助你轻松管理日常待办事项。支持创建、完成、删除任务，以及灵活设置任务的截止时间。

## ✨ 主要功能

- 📝 创建待办事项（可选设置截止时间）
- ✅ 完成待办事项
- 🗑️ 删除待办事项
- ⏰ 修改任务截止时间
- 📋 查看未完成的任务
- 📅 查看今天需要完成的任务
- 🔗 保存链接
- 🔔 每日提醒未读链接数量
- 🤖 AI 总结链接内容
- ❓ AI 解释链接内容

## 📖 使用指南

### 创建任务

创建任务有两种方式：

1. 直接发送任务内容（无截止时间）：

<div align="center">
  <img src="https://pic.rxlearn.site/2025/02/IMG_0653.jpg" width="400" alt="创建任务示例"/>
</div>

2. 设置截止时间的任务：

> 温馨提示：如果只填写日期，系统会默认设置为当天 18:00

<div align="center">
  <img src="https://pic.rxlearn.site/2025/02/IMG_0649.jpg" width="400" alt="设置截止时间示例"/>
</div>

### 完成任务

```
done 1
```

> 将编号为 1 的任务标记为已完成

<div align="center">
  <img src="https://pic.rxlearn.site/2025/02/IMG_0652.jpg" width="400" alt="完成任务示例"/>
</div>

### 删除任务

```
delete 1
```

> 删除编号为 1 的任务

<div align="center">
  <img src="https://pic.rxlearn.site/2025/02/IMG_0651.jpg" width="400" alt="删除任务示例"/>
</div>

### 修改截止时间

```
change endtime 1 2024-01-20
```

或

```
change endtime 1 2024-01-20 14:30
```

> 时间部分可选，默认为 18:00

### 查询待办事项

1. 查看所有待办事项（包括已完成）：

```
/demo
```

<div align="center">
  <img src="https://pic.rxlearn.site/2025/02/IMG_0654.png" width="360" alt="查看所有任务示例"/>
</div>

2. 只查看未完成的待办事项：

```
/demoz
```

<div align="center">
  <img src="https://pic.rxlearn.site/2025/02/IMG_0655.png" width="360" alt="查看未完成任务示例"/>
</div>

### 链接管理

1. **保存链接**

   直接发送链接给机器人，它会自动保存。

2. **每日提醒**

   每天定时提醒您有多少未读链接。

3. **AI 总结链接**
   ```
   /summarize
   ```
   > 机器人会随机选择一个未读链接，并使用 AI 进行总结。

4. **AI 解释链接**
   ```
   /explain [链接]
   ```
   > 机器人会使用 AI 解释您提供的链接内容。

### 配置 AI API Key 和代理地址

您需要自行设置 AI API Key 和代理地址，以便使用 AI 总结和解释功能。具体设置方法请参考机器人的配置文档。

## 📌 使用提示

- ⏰ 创建或修改任务时，截止时间必须晚于当前时间
- ⚠️ 已完成的任务不能修改截止时间
- 💡 如果只提供日期不提供时间，系统会默认使用当天 18:00
- 🕐 所有时间均使用 24 小时制

## ❗ 常见提示

机器人会在以下情况给出友好提示：

- 任务不存在
- 任务已完成
- 截止时间格式错误
- 截止时间早于当前时间
- 任务内容为空

## 🛠️ 技术架构

- Python
- python-telegram-bot
- SQLAlchemy
- PostgreSQL

## 💻 环境要求

- Python 3.7+
- PostgreSQL 数据库
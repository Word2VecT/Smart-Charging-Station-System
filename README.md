# 充电桩计费系统

本项目是一个智能充电桩计费和管理系统，包括一个 FastAPI 后端和一个 Nuxt.js 前端。

## 目录结构

```
.
├── backend/      # FastAPI 后端应用
├── frontend/     # Nuxt.js 前端应用
└── README.md
```

## 技术栈

- **后端**: Python 3.12, FastAPI, SQLAlchemy, `uv`
- **前端**: Nuxt.js 3, Vuetify, `bun`
- **数据库**: PostgreSQL 17

---

## 开发环境搭建

请按照以下步骤设置本地开发环境。

### 1. 环境准备

在开始之前，请确保您的系统上已安装以下工具：

> uv、bun 和 PostgreSQL 都可以用 Homebrew、scoop 或 apt 安装，highly recommend.

- **Python** (>= 3.10): [官方网站](https://www.python.org/)
- **uv**: Python 包管理器。请访问 [官方网站](https://docs.astral.sh/uv/) 获取安装说明。
- **Bun**: JavaScript 运行时和工具包。请访问 [官方网站](https://bun.sh/) 获取安装说明。
- **PostgreSQL**: 数据库服务。推荐使用 [Homebrew](https://brew.sh/) (macOS) 或 [scoop](https://scoop.sh/) (Windows) 或 apt-get (Ubuntu) 等进行安装。

### 2. 数据库设置

本项目使用 PostgreSQL 作为数据库。

1.  **安装并启动 PostgreSQL**，示例是在 macOS 上使用 Homebrew 进行设置的步骤。对于其他操作系统，请参考其官方文档，或者用 scoop 安装时应该会有启动后台服务的提示。核心就是启动后台服务。

    ```sh
    brew install postgresql@17
    brew services start postgresql@17
    ```

2.  **创建数据库用户和数据库**，下面的核心是创建一个和代码一致的数据库，从而避免修改代码，这个应该 windows 上可以直接用。

    您需要创建一个与项目配置匹配的用户 (`tang`) 和数据库 (`charge`)。

    首先，使用 `psql` 连接到默认的 `postgres` 数据库：
    ```sh
    psql postgres
    ```

    然后，在 `psql` 提示符中执行以下 SQL 命令：
    ```sql
    CREATE USER tang;
    CREATE DATABASE charge OWNER tang;
    -- 退出 psql
    \q
    ```

    上述操作可以保证配置信息如下所示：
    - **主机**: `localhost`
    - **端口**: `5432`（默认）
    - **用户名**: `tang`
    - **密码**: (无)
    - **数据库名**: `charge`

### 3. 后端设置

后端服务位于 `backend/` 目录下。

1.  **进入后端目录**
    ```sh
    cd backend
    ```

2.  **创建并激活虚拟环境**

    使用 `uv` 创建一个新的虚拟环境。
    ```sh
    uv venv
    ```

    激活虚拟环境：
    - 在 macOS / Linux 上:
      ```sh
      source .venv/bin/activate
      ```
    - 在 Windows (CMD) 上:
      ```sh
      .venv\Scripts\activate.bat
      ```

3.  **安装依赖**

    使用 `uv sync` 安装 `pyproject.toml` 中定义的所有依赖项。
    ```sh
    uv sync
    ```

4.  **初始化数据库**

    确保 PostgreSQL 服务正在运行，然后运行以下脚本来创建数据表：
    ```sh
    python create_db.py
    ```

5.  **运行后端开发服务器**

    一切就绪后，使用 `uvicorn` 启动开发服务器。
    ```sh
    uvicorn main:app --reload
    ```
    服务器将在 `http://127.0.0.1:8000` 上运行。您可以在 `http://127.0.0.1:8000/docs` 查看 API 文档。

### 4. 前端设置

前端应用位于 `frontend/` 目录下。

1.  **进入前端目录**

    在**新的终端窗口**中，进入 `frontend` 目录。
    ```sh
    cd frontend
    ```

2.  **安装依赖**

    使用 `bun` 安装所有依赖项。
    ```sh
    bun install
    ```

3.  **运行前端开发服务器**

    启动 Nuxt.js 开发服务器。
    ```sh
    bun dev
    ```
    前端应用将在 `http://localhost:3000` 上可用。

---

## 快速启动摘要

1.  **确保已经启动数据库**:
2.  **启动后端**:
    ```sh
    cd backend
    source .venv/bin/activate
    python create_db.py # 仅首次需要
    uv run fastapi dev
    ```

现在，您可以访问 `http://localhost:3000` 查看正在运行的应用程序。 
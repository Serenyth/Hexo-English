# 获取 essay.yml 内容的 API 实现思路

## 1. 目标

创建一个 FastAPI 后端 API 接口，用于读取项目 `source/_data/essay.yml` 文件内容，并将其处理后以 JSON 格式返回给前端。

## 2. 文件定位

*   **配置文件**: 需要确定博客项目的主配置文件路径（例如 `config.yml` 或类似文件），该文件应包含博客源文件目录 (`source_dir`) 的配置。
*   **拼接路径**: 后端 API 需要读取此配置文件，获取 `source_dir` 的值，然后拼接出 `essay.yml` 的完整路径：`os.path.join(source_dir, '_data', 'essay.yml')`。

## 3. 数据处理

*   **YAML 解析**: 使用 `PyYAML` 库来读取和解析 `essay.yml` 文件。需要确保已安装该库 (`pip install PyYAML`) 并将其添加到 `requirements.txt`。
*   **数据结构**:
    *   YAML 文件包含根级配置字段（如 `title`, `subTitle` 等）和 `essay_list` 数组。
    *   API 应返回一个 JSON 对象，包含两个主要部分：
        *   `settings`: 包含 YAML 文件中的根级配置字段。
        *   `essays`: 包含 `essay_list` 数组的内容。
*   **示例返回结构**:
    ```json
    {
      "settings": {
        "title": "即刻短文",
        "subTitle": "咸鱼的日常生活。",
        "tips": "随时随地，分享生活",
        "buttonText": "关于我",
        "buttonLink": "/about/",
        "limit": 30,
        "home_essay": true,
        "top_background": "https://..."
      },
      "essays": [
        {
          "content": "安知鱼主题指南",
          "date": "2023/09/09",
          "video": ["https://..."],
          // ... 其他可选字段
        },
        {
          "content": "支持了Accesskey快捷键...",
          "date": "2023/07/01",
          // ... 其他字段
        }
        // ... 更多 essay 条目
      ]
    }
    ```

## 4. API 实现 (FastAPI)

*   **创建路由**: 在 `backend/app/api/` 目录下创建新文件 `essays.py`（或在现有 `posts.py` 中添加，但建议分离）。
*   **定义 Endpoint**: 添加一个新的 GET 请求路由，例如 `@router.get("/essays", response_model=EssayResponse)`。
*   **实现逻辑**:
    1.  导入必要的库 (`os`, `yaml`, `FastAPI`, `HTTPException` 等)。
    2.  定义 Pydantic 模型 (`EssayItem`, `EssaySettings`, `EssayResponse`) 来校验和格式化返回数据。
    3.  实现读取配置文件、定位 `essay.yml`、解析 YAML 的逻辑。
    4.  处理文件未找到 (`FileNotFoundError`) 或 YAML 解析错误 (`yaml.YAMLError`) 的情况，返回适当的 HTTP 错误（如 404 或 500）。
    5.  成功时，将解析后的数据构造成 `EssayResponse` 模型并返回。
*   **注册路由**: 将新的 `essays` 路由添加到主 `app/main.py` 或相应的 API 路由器中。

## 5. 依赖管理

*   确保 `PyYAML` 已添加到项目的 `requirements.txt` 文件中。

## 6. 前端调用

*   前端可以通过向 `/api/essays` 发送 GET 请求来获取数据，并根据返回的 `settings` 和 `essays` 渲染页面。
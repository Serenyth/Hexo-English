#暂时不用，创建文章变更bug:会增加符号{}[]，内容不符合规范
import os
import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import Body

# 尝试从 blog.py 导入 load_config，如果失败则尝试从 utils.config 导入
# 注意：这假设 load_config 返回博客的根目录路径
try:
    from .blog import load_config
except ImportError:
    try:
        # 如果 blog.py 中没有，尝试从 utils 包导入（需要确认 utils.config 是否存在且有 load_blog_config）
        # 这里假设 utils.config.py 存在且有 load_blog_config 函数返回配置字典
        from ..utils.config import load_blog_config

        def load_config():
            config = load_blog_config()
            return config.get('directory') if config else None
    except ImportError:
        # 如果两者都失败，定义一个存根函数或引发更明确的错误
        print("警告：无法找到 load_config 函数。将无法加载博客目录路径。")
        def load_config():
            return None

router = APIRouter()

# Pydantic 模型定义
class AplayerConfig(BaseModel):
    server: Optional[str] = None
    id: Optional[str] = None

class EssayItem(BaseModel):
    content: str
    date: str
    video: Optional[List[str]] = None
    image: Optional[List[str]] = None
    address: Optional[str] = None
    from_: Optional[str] = Field(None, alias='from') # 处理 'from' 关键字
    link: Optional[str] = None
    aplayer: Optional[AplayerConfig] = None

class EssaySettings(BaseModel):
    title: Optional[str] = None
    subTitle: Optional[str] = None
    tips: Optional[str] = None
    buttonText: Optional[str] = None
    buttonLink: Optional[str] = None
    limit: Optional[int] = None
    home_essay: Optional[bool] = None
    top_background: Optional[str] = None

class EssayResponse(BaseModel):
    settings: EssaySettings
    essays: List[EssayItem]

# Pydantic 模型定义 - 用于创建新 Essay
class NewEssayPayload(BaseModel):
    content: str
    video: Optional[List[str]] = None
    image: Optional[List[str]] = None
    address: Optional[str] = None
    from_: Optional[str] = Field(None, alias='from') # 处理 'from' 关键字
    link: Optional[str] = None
    aplayer: Optional[AplayerConfig] = None

@router.get("/essays", response_model=EssayResponse, summary="获取碎碎念页面数据")
async def get_essays():
    """
    读取并返回 `source/_data/essay.yml` 的内容。
    现在支持根结构为列表的 YAML 文件。
    """
    blog_dir = load_config()
    if not blog_dir:
        raise HTTPException(status_code=500, detail="博客目录未配置或无法加载配置")

    essay_file_path = os.path.join(blog_dir, 'source', '_data', 'essay.yml')

    if not os.path.exists(essay_file_path):
        raise HTTPException(status_code=404, detail=f"Essay 文件未找到: {essay_file_path}")

    try:
        with open(essay_file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=500, detail=f"YAML 文件解析错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件时发生错误: {e}")

    # 检查数据是否为列表且不为空
    if not isinstance(data, list) or not data:
         raise HTTPException(status_code=500, detail="YAML 文件根结构不是预期的列表格式或文件为空")

    # 假设列表的第一个元素包含设置信息
    settings_data = data[0] if isinstance(data[0], dict) else {}
    # 列表的其余元素是文章条目
    essays_data = []
    for item in data:
        if isinstance(item, dict) and 'essay_list' in item:
            essays_data = item['essay_list']
            break

    # 验证并构造响应
    try:
        # 从第一个字典中提取设置，不存在的键将使用 Pydantic 模型的默认值 None
        settings = EssaySettings(**settings_data)
        # Pydantic 会自动处理 essays_data 列表中的字典到 EssayItem 的转换
        # 注意：确保 EssayItem 模型能正确处理 essays_data 中每个字典的结构
        response = EssayResponse(settings=settings, essays=essays_data)
    except Exception as e:
        # Pydantic 验证错误或其他构造错误
        raise HTTPException(status_code=500, detail=f"数据模型验证失败: {e}")

    return response

@router.post("/essays", summary="创建新的碎碎念条目")
async def create_essay(payload: NewEssayPayload = Body(...)):
    """
    接收新的碎碎念内容并将其追加到 `source/_data/essay.yml` 文件中的 `essay_list`。
    """
    blog_dir = load_config()
    if not blog_dir:
        raise HTTPException(status_code=500, detail="博客目录未配置或无法加载配置")

    essay_file_path = os.path.join(blog_dir, 'source', '_data', 'essay.yml')

    data = []
    settings_data = {}
    essay_list_data = []
    essay_list_index = -1 # 用于记录包含 essay_list 的字典在 data 中的索引

    try:
        if os.path.exists(essay_file_path):
            with open(essay_file_path, 'r', encoding='utf-8') as f:
                loaded_data = yaml.safe_load(f)
                if isinstance(loaded_data, list) and loaded_data:
                    data = loaded_data
                    # 查找设置和 essay_list
                    if isinstance(data[0], dict) and 'essay_list' not in data[0]: # 第一个元素通常是设置
                        settings_data = data[0]
                    for i, item in enumerate(data):
                        if isinstance(item, dict) and 'essay_list' in item:
                            essay_list_data = item['essay_list']
                            essay_list_index = i
                            break
                elif loaded_data is None or (isinstance(loaded_data, list) and not loaded_data):
                    print(f"警告：Essay 文件 '{essay_file_path}' 为空或格式不正确，将重新初始化。")
                    data = [settings_data, {'essay_list': essay_list_data}] # 初始化结构
                    essay_list_index = 1
                else:
                    raise HTTPException(status_code=500, detail=f"Essay 文件 '{essay_file_path}' 根结构不是预期的列表格式")
        else:
            print(f"信息：Essay 文件 '{essay_file_path}' 不存在，将创建并初始化。")
            data = [settings_data, {'essay_list': essay_list_data}] # 初始化结构
            essay_list_index = 1

    except yaml.YAMLError as e:
        raise HTTPException(status_code=500, detail=f"YAML 文件解析错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取或解析 Essay 文件时发生错误: {e}")

    # 如果加载后没有找到 essay_list 结构，则创建它
    if essay_list_index == -1:
        if not data: # 如果 data 为空（例如，文件只包含 `[]`）
            data.append(settings_data) # 添加空的 settings
        data.append({'essay_list': essay_list_data})
        essay_list_index = len(data) - 1

    # 创建新 essay 字典, 过滤掉值为 None 的键
    new_essay_raw = payload.dict(by_alias=True) # 使用 by_alias=True 来正确处理 'from_' -> 'from'
    new_essay = {k: v for k, v in new_essay_raw.items() if v is not None}
    new_essay['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 追加新 essay 到 essay_list
    # 确保 essay_list_data 是列表
    if not isinstance(data[essay_list_index]['essay_list'], list):
        data[essay_list_index]['essay_list'] = []
    data[essay_list_index]['essay_list'].append(new_essay)

    # 写回 YAML 文件
    try:
        # 使用自定义 Dumper 来更好地控制输出格式，例如缩进
        # PyYAML 默认的 dump 可能格式不太理想，但功能上是正确的
        # 如果需要更精细的格式控制，可以研究 ruamel.yaml
        with open(essay_file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=None, indent=2) # 添加 indent=2 改善可读性
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"写入 Essay 文件时发生错误: {e}")

    return {"message": "碎碎念创建成功"}

# --- 下面添加更新 API ---

class UpdateEssayPayload(BaseModel):
    content: Optional[str] = None
    video: Optional[List[str]] = None
    image: Optional[List[str]] = None
    address: Optional[str] = None
    from_: Optional[str] = Field(None, alias='from')
    link: Optional[str] = None
    aplayer: Optional[AplayerConfig] = None

class UpdateSettingsPayload(BaseModel):
    title: Optional[str] = None
    subTitle: Optional[str] = None
    tips: Optional[str] = None
    buttonText: Optional[str] = None
    buttonLink: Optional[str] = None
    limit: Optional[int] = None
    home_essay: Optional[bool] = None
    top_background: Optional[str] = None

@router.put("/essays/settings", summary="更新碎碎念设置信息")
async def update_settings(payload: UpdateSettingsPayload = Body(...)):
    """
    更新 `source/_data/essay.yml` 文件中的设置信息。
    """
    blog_dir = load_config()
    if not blog_dir:
        raise HTTPException(status_code=500, detail="博客目录未配置或无法加载配置")

    essay_file_path = os.path.join(blog_dir, 'source', '_data', 'essay.yml')

    if not os.path.exists(essay_file_path):
        raise HTTPException(status_code=404, detail=f"Essay 文件未找到: {essay_file_path}")

    try:
        with open(essay_file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=500, detail=f"YAML 文件解析错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件时发生错误: {e}")

    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise HTTPException(status_code=500, detail="Essay 文件格式不正确，无法找到设置信息")

    settings_data = data[0]
    update_data = payload.dict(exclude_unset=True) # 只获取显式设置的字段

    for key, value in update_data.items():
        settings_data[key] = value

    # 写回 YAML 文件
    try:
        with open(essay_file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=None, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"写入 Essay 文件时发生错误: {e}")

    return {"message": "设置更新成功"}

@router.put("/essays/{essay_index}", summary="更新指定索引的碎碎念条目")
async def update_essay(essay_index: int, payload: UpdateEssayPayload = Body(...)):
    """
    更新 `source/_data/essay.yml` 文件中指定索引的碎碎念条目。
    索引从 0 开始计算。
    """
    blog_dir = load_config()
    if not blog_dir:
        raise HTTPException(status_code=500, detail="博客目录未配置或无法加载配置")

    essay_file_path = os.path.join(blog_dir, 'source', '_data', 'essay.yml')

    if not os.path.exists(essay_file_path):
        raise HTTPException(status_code=404, detail=f"Essay 文件未找到: {essay_file_path}")

    try:
        with open(essay_file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=500, detail=f"YAML 文件解析错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件时发生错误: {e}")

    if not isinstance(data, list) or len(data) < 2:
        raise HTTPException(status_code=500, detail="Essay 文件格式不正确或缺少 essay_list 结构")

    essay_list_data = None
    essay_list_index_in_data = -1
    for i, item in enumerate(data):
        if isinstance(item, dict) and 'essay_list' in item:
            essay_list_data = item['essay_list']
            essay_list_index_in_data = i
            break

    if essay_list_data is None or not isinstance(essay_list_data, list):
         raise HTTPException(status_code=500, detail="在 Essay 文件中未找到 'essay_list' 或其格式不正确")

    if essay_index < 0 or essay_index >= len(essay_list_data):
        raise HTTPException(status_code=404, detail=f"索引 {essay_index} 超出范围")

    # 获取要更新的 essay
    essay_to_update = essay_list_data[essay_index]
    if not isinstance(essay_to_update, dict):
         raise HTTPException(status_code=500, detail=f"索引 {essay_index} 处的条目格式不正确")

    # 获取更新数据，只包含显式设置的字段，并处理别名 'from_'
    update_data = payload.dict(exclude_unset=True, by_alias=True)

    # 更新字段，只更新 payload 中非 None 的值
    for key, value in update_data.items():
        essay_to_update[key] = value

    # 添加更新时间戳 (可选)
    # essay_to_update['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 写回 YAML 文件
    try:
        with open(essay_file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=None, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"写入 Essay 文件时发生错误: {e}")

    return {"message": f"索引 {essay_index} 的碎碎念更新成功"}

# --- 可以添加 DELETE API ---
@router.delete("/essays/{essay_index}", summary="删除指定索引的碎碎念条目")
async def delete_essay(essay_index: int):
    """
    删除 `source/_data/essay.yml` 文件中指定索引的碎碎念条目。
    索引从 0 开始计算。
    """
    blog_dir = load_config()
    if not blog_dir:
        raise HTTPException(status_code=500, detail="博客目录未配置或无法加载配置")

    essay_file_path = os.path.join(blog_dir, 'source', '_data', 'essay.yml')

    if not os.path.exists(essay_file_path):
        raise HTTPException(status_code=404, detail=f"Essay 文件未找到: {essay_file_path}")

    try:
        with open(essay_file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=500, detail=f"YAML 文件解析错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件时发生错误: {e}")

    if not isinstance(data, list) or len(data) < 2:
        raise HTTPException(status_code=500, detail="Essay 文件格式不正确或缺少 essay_list 结构")

    essay_list_data = None
    essay_list_index_in_data = -1
    for i, item in enumerate(data):
        if isinstance(item, dict) and 'essay_list' in item:
            essay_list_data = item['essay_list']
            essay_list_index_in_data = i
            break

    if essay_list_data is None or not isinstance(essay_list_data, list):
         raise HTTPException(status_code=500, detail="在 Essay 文件中未找到 'essay_list' 或其格式不正确")

    if essay_index < 0 or essay_index >= len(essay_list_data):
        raise HTTPException(status_code=404, detail=f"索引 {essay_index} 超出范围")

    # 删除指定索引的 essay
    del essay_list_data[essay_index]

    # 写回 YAML 文件
    try:
        with open(essay_file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=None, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"写入 Essay 文件时发生错误: {e}")

    return {"message": f"索引 {essay_index} 的碎碎念删除成功"}
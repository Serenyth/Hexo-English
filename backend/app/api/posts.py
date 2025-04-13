# 导入所需的模块和类
from fastapi import APIRouter, HTTPException, Body, Form, Request  # FastAPI框架相关组件
from fastapi.responses import JSONResponse  # JSON响应处理
from typing import List, Optional, Dict, Any  # 类型注解
import os  # 文件系统操作
import json  # JSON数据处理
import frontmatter  # Markdown文件前置数据处理
from datetime import datetime  # 日期时间处理
from pathlib import Path  # 路径处理
import re  # 正则表达式
import yaml  # YAML数据处理
import aiofiles  # 异步文件操作

# 创建路由实例
router = APIRouter()

def format_date(date_value):
    """
    统一日期格式，将各种日期格式转换为字符串
    @param date_value: 日期值，可以是datetime对象或字符串
    @return: 格式化后的日期字符串
    """
    if isinstance(date_value, datetime):
        return date_value.isoformat()
    elif isinstance(date_value, str):
        try:
            return datetime.fromisoformat(date_value).isoformat()
        except ValueError:
            return date_value
    return ""

async def get_current_blog_path() -> Optional[str]:
    """
    获取当前选择的博客目录
    @return: 博客目录路径或None
    """
    try:
        # 使用与blog.py相同的配置文件路径
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
        config_path = os.path.join(config_dir, 'blog_config.json')
        if not os.path.exists(config_path):
            return None
            
        # 异步读取配置文件
        async with aiofiles.open(config_path, "r", encoding="utf-8") as f:
            content = await f.read()
            config = json.loads(content)
            return config.get("directory")
    except Exception as e:
        print(f"获取博客目录失败: {str(e)}")
        return None

@router.get("/list")
async def list_posts(request: Request = None):
    """
    获取所有文章列表
    @return: 包含所有文章信息的列表
    """
    blog_path = await get_current_blog_path()
    if not blog_path:
        raise HTTPException(status_code=404, detail="尚未选择博客目录")
    
    # 构建文章和草稿目录路径
    posts_dir = os.path.join(blog_path, "source", "_posts")
    drafts_dir = os.path.join(blog_path, "source", "_drafts")
    
    posts = []
    
    # 获取已发布的文章
    if os.path.exists(posts_dir):
        for filename in os.listdir(posts_dir):
            if filename.endswith(".md"):
                file_path = os.path.join(posts_dir, filename)
                try:
                    # 使用frontmatter解析Markdown文件
                    post = frontmatter.load(file_path)
                    # 构建文章数据结构
                    post_data = {
                        "filename": filename,
                        "title": post.get("title", "无标题"),
                        "date": format_date(post.get("date", "")),
                        "updated": format_date(post.get("updated", "")),
                        "tags": post.get("tags", []),
                        "categories": post.get("categories", []),
                        "status": "published",
                        "cover": post.get("cover", ""),
                        "path": file_path
                    }
                    posts.append(post_data)
                except Exception as e:
                    continue

    # 获取草稿文章
    if os.path.exists(drafts_dir):
        for filename in os.listdir(drafts_dir):
            if filename.endswith(".md"):
                file_path = os.path.join(drafts_dir, filename)
                try:
                    post = frontmatter.load(file_path)
                    post_data = {
                        "filename": filename,
                        "title": post.get("title", "无标题"),
                        "date": format_date(post.get("date", "")),
                        "updated": format_date(post.get("updated", "")),
                        "tags": post.get("tags", []),
                        "categories": post.get("categories", []),
                        "status": "draft",
                        "cover": post.get("cover", ""),
                        "path": file_path
                    }
                    posts.append(post_data)
                except Exception as e:
                    continue
    
    # 按日期排序（最新的在前）
    posts.sort(key=lambda x: x.get("date", "") or "", reverse=True)
    
    return posts

@router.get("/detail/{filename}")
async def get_post_detail(filename: str, request: Request = None):
    """
    获取文章详情
    """
    blog_path = await get_current_blog_path()
    if not blog_path:
        raise HTTPException(status_code=404, detail="尚未选择博客目录")
    
    # 检查文章是否在已发布目录
    posts_path = os.path.join(blog_path, "source", "_posts", filename)
    drafts_path = os.path.join(blog_path, "source", "_drafts", filename)
    
    file_path = None
    status = None
    
    if os.path.exists(posts_path):
        file_path = posts_path
        status = "published"
    elif os.path.exists(drafts_path):
        file_path = drafts_path
        status = "draft"
    else:
        raise HTTPException(status_code=404, detail=f"文章 {filename} 不存在")
    
    try:
        post = frontmatter.load(file_path)
        post_data = {
            "filename": filename,
            "title": post.get("title", "无标题"),
            "date": format_date(post.get("date", "")),
            "updated": format_date(post.get("updated", "")),
            "tags": post.get("tags", []) if isinstance(post.get("tags"), list) else [],
            "categories": post.get("categories", []) if isinstance(post.get("categories"), list) else [],
            "content": post.content,
            "status": status,
            "author": post.get("author", ""),
            "layout": post.get("layout", "post"),
            "comments": post.get("comments", True),
            "description": post.get("description", ""),
            "keywords": post.get("keywords", []),
            "top": post.get("top", False),
            "cover": post.get("cover", ""),
            "path": file_path
        }
        
        # 获取所有自定义字段
        custom_fields = {}
        for key, value in post.metadata.items():
            if key not in post_data:
                custom_fields[key] = value
        post_data["customFields"] = custom_fields
        
        return post_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析文章失败: {str(e)}")

@router.post("/create")
async def create_post(title: str = Form(...), content: str = Form(""), tags: str = Form(""), categories: str = Form(""), cover: str = Form(""), request: Request = None):
    """
    创建新文章
    @param title: 文章标题（必填）
    @param content: 文章内容（可选）
    @param tags: 文章标签，逗号分隔（可选）
    @param categories: 文章分类，逗号分隔（可选）
    @param cover: 文章封面图片（可选）
    @return: 创建结果
    """
    blog_path = await get_current_blog_path()
    if not blog_path:
        raise HTTPException(status_code=404, detail="尚未选择博客目录")
    
    # 确保文章目录存在
    posts_dir = os.path.join(blog_path, "source", "_posts")
    if not os.path.exists(posts_dir):
        os.makedirs(posts_dir)
    
    # 生成文件名（使用标题的拼音或英文，这里简化处理）
    filename = re.sub(r'[^\w\s]', '', title.lower()).replace(' ', '-')
    if not filename:
        filename = f"post-{datetime.now().strftime('%Y%m%d%H%M%S')}"  # 使用时间戳作为文件名
    
    filename = f"{filename}.md"
    file_path = os.path.join(posts_dir, filename)
    
    # 检查文件是否已存在
    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail=f"文件 {filename} 已存在")
    
    # 解析标签和分类
    tags_list = [tag.strip() for tag in tags.split(',')] if tags else []
    categories_list = [cat.strip() for cat in categories.split(',')] if categories else []
    
    # 创建frontmatter并设置文章元数据
    post = frontmatter.Post(content)
    post['title'] = title
    post['date'] = datetime.now()
    post['updated'] = datetime.now()
    post['tags'] = tags_list
    post['categories'] = categories_list
    post['cover'] = cover
    
    # 写入文件
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        return {"message": "文章创建成功", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建文章失败: {str(e)}")

@router.put("/update/{filename}")
async def update_post(
    filename: str,  # 文章文件名
    title: str = Form(...),  # 文章标题（必填）
    content: str = Form(...),  # 文章内容（必填）
    tags: str = Form(""),  # 文章标签，逗号分隔
    categories: str = Form(""),  # 文章分类，逗号分隔
    status: str = Form("draft"),  # 文章状态：published或draft
    date: str = Form(...),  # 发布日期（必填）
    updated: str = Form(...),  # 更新日期（必填）
    author: str = Form(""),  # 作者
    layout: str = Form("post"),  # 布局模板
    comments: bool = Form(True),  # 是否允许评论
    description: str = Form(""),  # 文章描述
    keywords: str = Form(""),  # 关键词，逗号分隔
    top: bool = Form(False),  # 是否置顶
    cover: str = Form(""),  # 封面图片
    customFields: str = Form("{}"),  # 自定义字段，JSON格式
    request: Request = None
):
    """更新文章
    接收前端表单数据，更新或移动文章文件
    @param filename: 文章文件名
    @param title: 文章标题
    @param content: 文章内容
    @param tags: 文章标签
    @param categories: 文章分类
    @param status: 文章状态
    @param date: 发布日期
    @param updated: 更新日期
    @param author: 作者
    @param layout: 布局模板
    @param comments: 是否允许评论
    @param description: 文章描述
    @param keywords: 关键词
    @param top: 是否置顶
    @param cover: 封面图片
    @param customFields: 自定义字段
    @return: 更新结果
    """
    try:
        # 获取当前选择的博客目录
        blog_path = await get_current_blog_path()
        if not blog_path:
            raise HTTPException(status_code=400, detail="请先选择博客目录")

        # 确定源文件和目标文件路径
        source_posts_dir = os.path.join(blog_path, "source", "_posts")
        source_drafts_dir = os.path.join(blog_path, "source", "_drafts")
        
        # 创建目录（如果不存在）
        os.makedirs(source_posts_dir, exist_ok=True)
        os.makedirs(source_drafts_dir, exist_ok=True)

        # 根据状态确定目标目录
        target_dir = source_posts_dir if status == "published" else source_drafts_dir
        
        # 查找当前文件位置
        current_file = None
        possible_locations = [
            os.path.join(source_posts_dir, filename),
            os.path.join(source_drafts_dir, filename)
        ]
        for loc in possible_locations:
            if os.path.exists(loc):
                current_file = loc
                break

        if not current_file:
            raise HTTPException(status_code=404, detail="文章不存在")

        # 构建文章 front-matter（文章元数据）
        front_matter = {
            "title": title,
            "date": date,
            "updated": updated,
            "tags": tags.split(",") if tags else [],
            "categories": categories.split(",") if categories else [],
            "author": author,
            "layout": layout,
            "comments": comments,
            "description": description,
            "keywords": keywords.split(",") if keywords else [],
            "top": top,
            "cover": cover
        }

        # 添加自定义字段
        custom_fields = json.loads(customFields)
        front_matter.update(custom_fields)

        # 生成 YAML 格式的 front-matter
        yaml_content = "---\n"
        yaml_content += yaml.dump(front_matter, allow_unicode=True)
        yaml_content += "---\n\n"
        yaml_content += content

        # 确定目标文件路径
        target_file = os.path.join(target_dir, filename)

        # 如果目标文件与当前文件不同，则需要移动文件
        if current_file != target_file:
            # 如果目标文件已存在，先删除
            if os.path.exists(target_file):
                os.remove(target_file)
            # 删除原文件（如果存在）
            if os.path.exists(current_file):
                os.remove(current_file)

        # 异步写入文件内容
        async with aiofiles.open(target_file, "w", encoding="utf-8") as f:
            await f.write(yaml_content)

        return {"message": "文章更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{filename}")
async def delete_post(filename: str, request: Request = None):
    """
    删除文章
    """
    blog_path = await get_current_blog_path()
    if not blog_path:
        raise HTTPException(status_code=404, detail="尚未选择博客目录")
    
    file_path = os.path.join(blog_path, "source", "_posts", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"文章 {filename} 不存在")
    
    try:
        os.remove(file_path)
        return {"message": "文章删除成功", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文章失败: {str(e)}")
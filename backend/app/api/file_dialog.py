from fastapi import APIRouter
from tkinter import Tk, filedialog
from typing import Optional
import os

router = APIRouter()

@router.get("/select_directory")
async def select_directory() -> dict:
    """打开系统文件选择对话框选择目录"""
    try:
        # 创建一个隐藏的Tk窗口
        root = Tk()
        root.withdraw()
        
        # 设置窗口置顶
        root.attributes('-topmost', True)
        root.lift()  # 提升窗口层级
        
        # 打开文件选择对话框
        directory = filedialog.askdirectory(
            title='选择博客目录',
            initialdir=os.path.expanduser('~')  # 默认从用户主目录开始
        )
        
        # 销毁Tk窗口
        root.destroy()
        
        if not directory:  # 用户取消选择
            return {"directory": None, "cancelled": True}
            
        return {"directory": directory, "cancelled": False}
        
    except Exception as e:
        return {"error": str(e)}
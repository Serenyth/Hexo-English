
@echo off
cd /d "E:\inisBlog"
echo 切换到博客目录: E:\inisBlog
echo 执行 hexo clean...
call hexo clean
echo 执行 hexo generate...
call hexo generate
echo 启动服务器...
call hexo server
pause

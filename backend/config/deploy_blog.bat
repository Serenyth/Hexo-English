
@echo off
cd /d "D:/inisBlog"
echo 切换到博客目录: D:/inisBlog
echo 执行 hexo clean...
call hexo clean
echo 执行 hexo generate...
call hexo generate
echo 开始部署...
call hexo deploy
echo 部署完成！
pause

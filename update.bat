@echo off
@chcp 65001 > lul
echo [1/3] 올리브영 랭킹 수집 시작...
python crawler.py

echo [2/3] 데이터를 및 소스코드 GitHub에 업로드 중...
git add data.json crawler.py update.bat
git commit -m "Update ranking data and scripts: %date% %time%"
git push

echo [3/3] 완료! 웹사이트가 곧 업데이트됩니다.
pause
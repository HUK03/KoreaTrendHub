@echo off
echo 크롤링 시작...
python crawler.py
echo GitHub에 업로드 중...
git add data.json
git commit -m "Update ranking data"
git push
echo 완료! 웹사이트가 곧 업데이트됩니다.
pause

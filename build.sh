cd /root/lianshu

git fetch origin
git merge origin/master

pip3 install -r requirements.txt

cd /root/lianshu/lianshu

python3 manage.py migrate --settings=lianshu.settings_prod
python3 manage.py collectstatic --no-input --settings=lianshu.settings_prod

supervisorctl restart lianshu
service nginx restart
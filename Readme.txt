dev_appserver.py ./

dev_appserver.py --datastore_path='./tmp/datastore.db' ./

gcloud app deploy index.yaml --project gladtidings-162622

Use the following command to deploy:

gcloud app deploy --project gladtidings-162622

appcfg.py --oauth2 -A gladtidings-162622 update ./ 



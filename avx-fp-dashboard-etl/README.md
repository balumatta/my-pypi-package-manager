# FP Dashboard ETL

The ETL process will read the data from the on-prem database and compare it with the data in the dashboard data store and
make the appropriate adds, updates, and deletes. It will be triggered whenever there is an update from the SSIS

### Project Setup

```
sudo apt-get update

sudo apt-get install virtualenv
sudo apt-get install --upgrade pip

https://git-codecommit.us-east-1.amazonaws.com/v1/repos/fp-dashboard-etl-lambda
cd fp-dashboard-etl-lambda

virtualenv --python=python3.9 venv
source venv/bin/activate

pip install -r requirements.txt
```

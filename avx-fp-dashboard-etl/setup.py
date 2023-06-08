import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='avx_fp_dashboard_etl',
    version='0.0.1',
    author='Avantax Wealth Management',
    author_email='balu.murthy@avantax.com',
    description='This is the FP Dashboard ETL Data Processor package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['avx-fp-dashboard-etl'],
    install_requires=['boto3==1.21.2', 'botocore==1.24.46', 'logging-config==1.0.4', 'packaging==23.0',
                      'pathlib==1.0.1', 'peewee==3.14.8', 'psycopg2-binary==2.9.3', 'python-dateutil==2.8.2',
                      'python-dotenv==1.0.0', 'python-json-logger==2.0.7', 'requests==2.28.2',
                      'splunk-handler==3.0.0', 'text-unidecode==1.3', 'urllib3==1.26.15'],
)

# #!/bin/bash
# # Install dependencies using the correct Python environment
# python3 -m pip install --upgrade pip  # Upgrade pip to ensure compatibility
# python3 -m pip install -r requirements.txt  # Install required dependencies

# # Run Django collectstatic to collect static files into STATIC_ROOT
# python3 manage.py collectstatic --noinput


#!/bin/bash
set -e

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
# pip uninstall mysqlclient

pip install -r requirements.txt
# python manage.py migrate --noinput #added to apply migrations
python manage.py collectstatic --noinput

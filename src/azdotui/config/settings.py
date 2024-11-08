# config/settings.py

import os

AZDO_ORGANIZATION = os.getenv('AZDO_ORGANIZATION', 'your_organization')
AZDO_PAT = os.getenv('AZDO_PAT', 'your_personal_access_token')


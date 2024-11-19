# SPDX-FileCopyrightText: 2024 Magenta ApS <info@magenta.dk>
#
# SPDX-License-Identifier: MPL-2.0
import os
from typing import List

from project.settings.base import BASE_DIR

# Static & uploaded files
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS: List[str] = []
# Max 2 MB - can be lower if we want
MAX_UPLOAD_FILESIZE = 22097152

#!/bin/bash

# Copyright 2019-2020 NVIDIA CORPORATION

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

PACKMAN_CMD="$(dirname "${BASH_SOURCE}")/packman"
if [ ! -f "$PACKMAN_CMD" ]; then
    PACKMAN_CMD="${PACKMAN_CMD}.sh"
fi
source "$PACKMAN_CMD" init
export PYTHONPATH="${PM_MODULE_DIR}:${PYTHONPATH}"
export PYTHONNOUSERSITE=1

# workaround for our python not shipping with certs
if [[ -z ${SSL_CERT_DIR:-} ]]; then
    export SSL_CERT_DIR=/etc/ssl/certs/
fi

D=$(dirname "${BASH_SOURCE}")
"${PM_PYTHON}" -m pip install -r ${D}/../../source/requirements.txt  --target=${D}/../../pip-packages
"${PM_PYTHON}" -u "$@"

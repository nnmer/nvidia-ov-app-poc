import sys
import subprocess
import json
import os

# print (os.environ)
# subprocess.run(["python3","--version"])
# res = subprocess.run(["python3","-c","import site; print(site.getsitepackages())"], stdout=subprocess.PIPE).stdout.decode().replace('\'','"')
# x=set(json.loads(res))
# #x.add('/home/ov/Dev/ov-app/venv/lib/python3.7/site-packages')
# x.add('/home/ov/.local/lib/python3.7/site-packages')
# print (x)
# for s in x:
#     if s.endswith('site-packages'):
#         print(f"Appending sys.path with {s}")
#         sys.path.append(f"{s}")

# sys.path.append('/usr/lib/python3/dist-packages')
# sys.path.append('/home/ov/.cache/packman/chk/kit-kernel/105.0.2+release.109455.818d8fa0.tc.linux-x86_64.release/python/lib/python3.10/site-packages')
# sys.path.append('/home/ov/.local/share/ov/data/Kit/my_name.my_app/1.0/pip3-envs/default')

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), f"..{os.sep}..{os.sep}..{os.sep}..{os.sep}..{os.sep}pip-packages"))

from dotenv import dotenv_values, find_dotenv, load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), f"..{os.sep}..{os.sep}..{os.sep}..{os.sep}.env")
load_dotenv(dotenv_path)

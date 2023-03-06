import sys
import subprocess
import json

res = subprocess.run(["py","-c","import site; print(site.getsitepackages())"], stdout=subprocess.PIPE).stdout.decode().replace('\'','"')
for s in set(json.loads(res)):
    if s.endswith('site-packages'):
        print(f"Appending sys.path with {s}")
        sys.path.append(f"{s}")

from dotenv import dotenv_values, find_dotenv, load_dotenv
import os

#print("SEEEEETTTTUUUPPPP ENVIIIIRONMENT!!!!!!!")

dotenv_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..\..\..\..\.env")
load_dotenv(dotenv_path)

#print(os.environ)

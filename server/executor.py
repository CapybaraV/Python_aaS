import threading
import requests
import tempfile
import os
import uuid
import json
import docker
from typing import Dict, Any

class ScriptExec:
    def __init__(self):
        self.execs = {}
        self.lock = threading.Lock()
    def download_script(self, url:str) -> str:
        response = requests.get(url)
        fd, path = tempfile.mkstemp(suffix='.py')
        with os.fdopen(fd, 'wb') as f:
            f.write(response.content)
        os.chmod(path, 0o755)
        return path
    def execute_sync(self, url:str, params:Dict[str, str]) ->Dict[str, Any]:
        exec_id = str(uuid.uuid4())
        full_path = None
        try:
            file = self.download_script(url)
            params_json = json.dumps(params)
            client = docker.from_env()
            full_path = os.path.abspath(file)
            dir = os.path.dirname(full_path)
            name = os.path.basename(full_path)
            if not os.path.exists(full_path):
                error_result = {
                    'exit_code': -1,
                    'output': '',
                    'stderr': f"'{file}' not found at {full_path}",
                    'execution_id': exec_id
                }
                return error_result
            
            container = client.containers.run(
                image="python:3.13-slim",
                command=["python", f"/scripts/{name}", params_json],
                detach=True,
                remove=False,
                mem_limit="128m",
                volumes={
                    dir: {
                        "bind": "/scripts",
                        "mode": "ro"
                    }
                }
            )

            result = container.wait(timeout=5)
            logs = container.logs(stdout=True, stderr=True)
            container.remove()
            os.remove(file)
            response_result = {
                "exit_code": result.get("StatusCode", "StatusCode not found"),
                "output": logs.decode(),
                "stderr": result.get('Error', ''),
                "exec_id": exec_id
            }
            return response_result
        except Exception as e:
            error_result = {
                'exit_code': -1,
                'output': '',
                'stderr': str(e),
                'execution_id': exec_id
            }
            return error_result
        
# test = ScriptExec()
# params = {
#         "start_x": 1,
#         "start_y": 1,
#         "end_x": 3,
#         "end_y": 2
#     }
# print(test.execute_sync("../script.py", params))

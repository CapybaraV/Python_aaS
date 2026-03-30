import threading
import requests
import tempfile
import os
import uuid
import json
import docker
import time
import logging
from typing import Dict, Any
class ScriptExec:
    def __init__(self):
        self.executions = {}
        self.lock = threading.Lock()
        self.client = docker.from_env()

    def download_script(self, url: str) -> str:
        print(f"Downloading script from: {url}", flush=True)
        response = requests.get(url)
        response.raise_for_status()
        script_name = f"{uuid.uuid4().hex}.py"
        path = os.path.join("/tmp/scripts", script_name)
        
        with open(path, "wb") as f:
            f.write(response.content)
        os.chmod(path, 0o755)
        print(path)
        return path

    def run_in_container(self, file_path: str, params: Dict[str, str]) -> Dict[str, Any]:
        full_path = os.path.abspath(file_path)
        dir_path = os.path.dirname(full_path)
        name = os.path.basename(full_path)
        print(name, dir_path, full_path)
        container = self.client.containers.run(
            image="python:3.13-slim",
            command=["python", f"/scripts/{name}", json.dumps(params)],
            detach=True,
            mem_limit="128m",
            nano_cpus=500_000_000,
            network_disabled=True,
            read_only=True,
            pids_limit=64,
            volumes={
                "/tmp/python-aas-scripts/": {
                    "bind": "/scripts",
                    "mode": "ro"
                }
            }
        )

        try:
            result = container.wait(timeout=8)

            stdout = container.logs(stdout=True, stderr=False).decode()
            stderr = container.logs(stdout=False, stderr=True).decode()
            print(stdout)
            return {
                "exit_code": result.get("StatusCode", -1),
                "output": stdout,
                "stderr": stderr
            }

        except Exception as e:
            container.kill()
            raise e

        finally:
            container.remove(force=True)

    def execute_sync(self, url: str, params: Dict[str, str]) -> Dict[str, Any]:
        exec_id = str(uuid.uuid4())
        file_path = None
        print(url)

        try:
            file_path = self.download_script(url)
            result = self.run_in_container(file_path, params)

            response = {
                **result,
                "execution_id": exec_id
            }

            with self.lock:
                self.executions[exec_id] = {
                    "status": "completed",
                    "result": response,
                    "timestamp": time.time()
                }

            return response

        except Exception as e:
            error = {
                "exit_code": -1,
                "output": "",
                "stderr": str(e),
                "execution_id": exec_id
            }

            with self.lock:
                self.executions[exec_id] = {
                    "status": "failed",
                    "result": error,
                    "timestamp": time.time()
                }

            return error

        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)

    def submit_async(self, url: str, params: Dict[str, str]) -> str:
        exec_id = str(uuid.uuid4())

        with self.lock:
            self.executions[exec_id] = {
                "status": "pending",
                "result": None,
                "timestamp": time.time()
            }

        thread = threading.Thread(
            target=self.execute_async,
            args=(exec_id, url, params),
            daemon=True
        )
        thread.start()

        return exec_id

    def execute_async(self, exec_id: str, url: str, params: Dict[str, str]):
        file_path = None

        try:
            with self.lock:
                self.executions[exec_id]["status"] = "running"

            file_path = self.download_script(url)

            result = self.run_in_container(file_path, params)

            response = {
                **result,
                "execution_id": exec_id
            }

            with self.lock:
                self.executions[exec_id] = {
                    "status": "completed",
                    "result": response,
                    "timestamp": time.time()
                }

        except Exception as e:
            print(str(e))
            with self.lock:
                self.executions[exec_id] = {
                    "status": "failed",
                    "result": {
                        "exit_code": -1,
                        "output": "",
                        "stderr": str(e),
                        "execution_id": exec_id
                    },
                    "timestamp": time.time()
                }

        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)

    def get_status(self, exec_id: str) -> Dict[str, str]:
        with self.lock:
            if exec_id not in self.executions:
                return {"status": "not_found"}

            return {"status": self.executions[exec_id]["status"]}

    def get_result(self, exec_id: str) -> Dict[str, Any]:
        with self.lock:
            if exec_id not in self.executions:
                return {"error": "not_found"}

            exec_info = self.executions[exec_id]

            result = exec_info["result"]
            return {
                "exit_code": result.get("exit_code", -1),
                "execution_id": result.get("execution_id", exec_id),
                "output": result.get("output", ""),
                "stderr": result.get("stderr", "")
            }
        

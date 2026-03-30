import docker
import json
import os

def run_script(file, params=None):
    if params is None:
        params = {}
    
    try:
        client = docker.from_env()
        full_path = os.path.abspath(file)
        dir = os.path.dirname(full_path)
        name = os.path.basename(full_path)
        if not os.path.exists(full_path):
            return -1, f"'{file}' not found at {full_path}"
        params_json = json.dumps(params)
        
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
        
        return result["StatusCode"], logs.decode()
        
    except docker.errors.ImageNotFound:
        return -1, "Docker image not found"
    except docker.errors.APIError as e:
        return -1, f"Docker error: {e}"
    except Exception as e:
        return -1, f"Error: {e}"


if __name__ == "__main__":
    params = {
        "start_x": 1,
        "start_y": 1,
        "end_x": 3,
        "end_y": 2
    }
    
    exit_code, output = run_script("script.py", params)
    print(f"exit code: {exit_code}")
    print(f"output:\n{output}")

    {"start_x": 1, "start_y": 1, "end_x": 2, "end_y": 2}
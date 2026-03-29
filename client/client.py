import grpc
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../server'))
import service_pb2
import service_pb2_grpc
import json

def call_execute_script():
    channel = grpc.insecure_channel('localhost:50051')
    stub = service_pb2_grpc.ScriptServiceStub(channel)
    params = {
            "start_x": 1,
            "start_y": 1,
            "end_x": 2,
            "end_y": 2
        }
    request = service_pb2.ScriptRequest(
        url="http://0.0.0.0:8000/script.py",
        params = json.dumps(params)
    )
    try:
        response = stub.ExecuteScript(request)
        print(response)
        return response
    except grpc.RpcError as e:
        print(f"{e.code()} - {e.details()}")
    except Exception as e:
        print(f"{e}")

if __name__ == "__main__":
    call_execute_script()
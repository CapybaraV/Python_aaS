import grpc
import service_pb2
import service_pb2_grpc
import json
from executor import ScriptExec
from concurrent import futures

class ScriptServiceServicer(service_pb2_grpc.ScriptServiceServicer):
    def __init__(self):
        self.executor = ScriptExec()
        
    def ExecuteScript(self, request, context):
        result = self.executor.execute_sync(
            request.url,
            json.loads(request.params)
        )
        # print(result)
        
        return service_pb2.ScriptResponse(
            exit_code = result["exit_code"],
            exec_id = result["exec_id"],
            result = result["output"],
            stderr = result["stderr"]
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ScriptServiceServicer_to_server(
        ScriptServiceServicer(), 
        server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
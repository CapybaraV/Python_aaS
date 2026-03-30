import grpc
import service_pb2
import service_pb2_grpc
import json
from executor import ScriptExec
from concurrent import futures

class ScriptServiceServicer(service_pb2_grpc.ScriptServiceServicer):
    def __init__(self):
        self.executor = ScriptExec()
        
    def ExecuteScriptSync(self, request, context):
        result = self.executor.execute_sync(
            request.url,
            json.loads(request.params)
        )

        return service_pb2.ScriptResponseSync(
            exit_code = result["exit_code"],
            exec_id = result["execution_id"],
            result = result["output"],
            stderr = result["stderr"]
        )
    def ExecuteScriptAsync(self, request, context):
        exec_id = self.executor.submit_async(
            request.url,
            json.loads(request.params)
        )

        return service_pb2.ScriptResponseAsync(
            exec_id = exec_id
        )
    def GetStatus(self, request, context):
        result = self.executor.get_status(
            request.exec_id
        )
        status = {
            "pending": service_pb2.PENDING,
            "running": service_pb2.RUNNING,
            "completed": service_pb2.COMPLETED,
            "failed": service_pb2.FAILED,
            "not_found": service_pb2.UNKNOWN
        }
        status_res = status.get(
            result.get("status", 'unknown'),
            service_pb2.UNKNOWN
        )
        return service_pb2.StatusResponse(
            exec_id = request.exec_id,
            status = status_res,
        )
    def GetResult(self, request, context):
        result = self.executor.get_result(
            request.exec_id
        )
        return service_pb2.ScriptResponseSync(
            exit_code = result["exit_code"],
            exec_id = result["execution_id"],
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
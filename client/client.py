import grpc
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../server'))
import service_pb2
import service_pb2_grpc
import json

class Client:
    def __init__(self, address='localhost:50051'):
        self.channel = grpc.insecure_channel(address)
        self.stub = service_pb2_grpc.ScriptServiceStub(self.channel)
    def input_url(self):
        url = input("Введите url:\n").strip()
        return url
    def input_params(self):
        params = input("Введите параметры в формате JSON:\n")
        try:
            params = json.loads(params)
            return params
        except Exception as e:
            print(e)
    def run_sync(self):
        request = service_pb2.ScriptRequest(
            url = self.input_url(),
            params = json.dumps(self.input_params())
        )
        try:
            response = self.stub.ExecuteScriptSync(request)
            print(response)
        except grpc.RpcError as e:
            print(f"{e.code()} - {e.details()}")
        except Exception as e:
            print(f"{e}")
    def run_async(self):
        request = service_pb2.ScriptRequest(
            url = self.input_url(),
            params = json.dumps(self.input_params())
        )
        try:
            response = self.stub.ExecuteScriptAsync(request)
            print(response)
        except grpc.RpcError as e:
            print(f"{e.code()} - {e.details()}")
        except Exception as e:
            print(f"{e}")
    def return_status(self):
        exec_id = input("Введите exec_id для получения результата:\n").strip()
        request = service_pb2.StatusRequest(
            exec_id = exec_id
        )
        try:
            status = self.stub.GetStatus(request)
            print(status)
        except grpc.RpcError as e:
            print(f"{e.code()} - {e.details()}")
        except Exception as e:
            print(f"{e}")
    def get_res(self):
        exec_id = input("Введите exec_id для получения результата:\n").strip()
        request = service_pb2.StatusRequest(
            exec_id = exec_id
        )
        try:
            response = self.stub.GetResult(request)
            print(response)
        except grpc.RpcError as e:
            print(f"{e.code()} - {e.details()}")
        except Exception as e:
            print(f"{e}")
    def run(self):
        print("===Python_aaS===\n")
        while True:
            print("Выберите действие:\n")
            print("1 - Sync запуск\n")
            print("2 - Async запуск\n")
            print("3 - Узнать статус\n")
            print("4 - Получить результат\n")
            print("0 - Выход\n")
            answer = input().strip()
            match answer:
                case '1':
                    self.run_sync()
                case '2':
                    self.run_async()
                case '3':
                    self.return_status()
                case '4':
                    self.get_res()
                case '0':
                    break
                case _:
                    print("Неверный ввод\n")




# def call_execute_script():
#     channel = grpc.insecure_channel('localhost:50051')
#     stub = service_pb2_grpc.ScriptServiceStub(channel)
    # params = {
    #         "start_x": 1,
    #         "start_y": 1,
    #         "end_x": 2,
    #         "end_y": 2
    #     }
#     request = service_pb2.ScriptRequest(
#         url="http://0.0.0.0:8000/script.py",
#         params = json.dumps(params)
#     )
#     try:
#         response = stub.ExecuteScript(request)
#         print(response)
#         return response
#     except grpc.RpcError as e:
#         print(f"{e.code()} - {e.details()}")
#     except Exception as e:
#         print(f"{e}")

def start_client():
    client = Client()
    client.run()


if __name__ == "__main__":
    start_client()
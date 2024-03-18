import grpc
import ClientServerComms_pb2
import ClientServerComms_pb2_grpc

if __name__ == "__main__":
    with grpc.insecure_channel("localhost:50050") as channel:
        stub = ClientServerComms_pb2_grpc.ClientServerCommsStub(channel)
        response = stub.Login(ClientServerComms_pb2.LoginRequest(username="", address=0x0, digitalSignature=bytes()))
        print(response)

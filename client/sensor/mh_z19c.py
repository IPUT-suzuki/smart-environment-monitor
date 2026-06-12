import serial

def get_mhz19c_data(port:str,rate:int,timeout:int):
    if not port:
        raise ValueError("MH-Z19C serial port is not set. Please check config.py")
    if not rate:
        raise ValueError("MH-Z19C baud rate is not set. Please check config.py")
    if timeout is None:
        raise ValueError("MH-Z19C timeout is not set. Please check config.py")
    ser = serial.Serial(port,rate,timeout)
    # CO2リクエストコマンド
    ser.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
    # 9バイト返ってくる
    data = ser.read(9)
    #独自でエラー返す
    if len(data) != 9:
        raise MHZ19CReadError(f"invalid length: {len(data)}")
    # CO2濃度（ppm）
    co2 = data[2] * 256 + data[3]
    return co2

class MHZ19CError(Exception):
    pass

class MHZ19CReadError(MHZ19CError):
    pass

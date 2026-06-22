import logging
import time

import serial

logger = logging.getLogger(__name__)


class MHZ19CSensor:
    def __init__(self, port: str, baudrate: int, timeout: float):
        self._serial = None
        try:
            self._serial = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
            logger.info("MH-Z19C ready")
        except Exception as error:
            logger.warning("MH-Z19C initialization failed: %s", error)

    def read(self) -> dict[str, int] | None:
        if self._serial is None:
            return None
        try:
            self._serial.reset_input_buffer()
            self._serial.write(bytes([0xFF, 0x01, 0x86, 0, 0, 0, 0, 0, 0x79]))
            time.sleep(0.1)
            response = self._serial.read(9)
            if len(response) != 9:
                logger.warning("MH-Z19C response length was %d, expected 9", len(response))
                return None
            return {"co2": response[2] * 256 + response[3]}
        except Exception as error:
            logger.warning("MH-Z19C read failed: %s", error)
            return None

    def close(self) -> None:
        if self._serial is not None:
            self._serial.close()

import signal
import os
import subprocess
from pathlib import Path


class MongoDBProcess:

    def __init__(self, dbpath: Path = Path('data/db'), host: str = 'localhost', port: int = 27017):
        self.dbpath = dbpath
        self.host = host
        self.port = port
        self.process = None

    def start(self):
        """
        Start the MongoDB server using the specified dbpath and port.
        """

        # Ensure the database path exists
        os.makedirs(self.dbpath, exist_ok=True)

        # Command to start MongoDB
        command = ['mongod', '--dbpath',
                   str(self.dbpath.absolute()), '--port', str(self.port)]

        print(' '.join(str(x) for x in command))

        # Start MongoDB as a subprocess
        self.process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f"MongoDB started with PID: {self.process.pid}")

    def stop(self):
        """
        Stop the MongoDB server.
        """
        if self.process is not None:
            # Send SIGTERM signal to the MongoDB process
            self.process.send_signal(signal.SIGTERM)
            self.process.wait()  # Wait for the process to terminate
            print("MongoDB server has been stopped")
            self.process = None
        else:
            print("MongoDB server is not running.")

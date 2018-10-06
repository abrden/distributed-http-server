import os
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(threadName)s: %(message)s")

from .audit_logger import AuditLogger


def main():
    l = AuditLogger(os.environ['FE_IP'], int(os.environ['FE_PORT']), os.environ['LOG_FILE'])
    l.start()


if __name__ == "__main__":
    main()

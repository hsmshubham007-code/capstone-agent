import os
import sqlite3

from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver


load_dotenv()


CHECKPOINT_DIR = os.getenv(
    "CHECKPOINT_DIR",
    "storage/checkpoints"
)

CHECKPOINT_DB = os.path.join(
    CHECKPOINT_DIR,
    "checkpoints.sqlite"
)


os.makedirs(
    CHECKPOINT_DIR,
    exist_ok=True
)


connection = sqlite3.connect(
    CHECKPOINT_DB,
    check_same_thread=False
)


checkpointer = SqliteSaver(connection)
from .chat import chat_comand
from .messages import doc_comand, state_comand, upload_comand

labelers = [
    doc_comand.labeler,
    state_comand.labeler,
    upload_comand.labeler,
    chat_comand.chat_labeler,
]

__all__ = ["labelers"]

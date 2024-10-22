<<<<<<< HEAD
from . import doc_comand, state_comand, upload_comand
=======
from .chat import chat_comand
from .messages import doc_comand, state_comand, upload_comand
>>>>>>> e8e5c707dd771d987fe5d48b30b449ff97b8ad85

labelers = [
    doc_comand.labeler,
    state_comand.labeler,
    upload_comand.labeler,
<<<<<<< HEAD
=======
    chat_comand.chat_labeler,
>>>>>>> e8e5c707dd771d987fe5d48b30b449ff97b8ad85
]

__all__ = ["labelers"]

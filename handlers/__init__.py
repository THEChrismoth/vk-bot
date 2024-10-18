from . import doc_comand, state_comand, upload_comand

labelers = [
    doc_comand.labeler,
    state_comand.labeler,
    upload_comand.labeler,
]

__all__ = ["labelers"]

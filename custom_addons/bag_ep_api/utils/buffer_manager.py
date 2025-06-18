# utils/buffer_manager.py
class BufferManager:
    _single = None

    @classmethod
    def set(cls, parsed):
        cls._single = parsed

    @classmethod
    def get(cls):
        return cls._single

    @classmethod
    def clear(cls):
        cls._single = None

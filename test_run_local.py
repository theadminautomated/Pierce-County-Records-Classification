from fastapi import FastAPI
import types
import sys



import importlib.machinery


class DummyTorch(types.ModuleType):
    pass

    class cuda:
        @staticmethod
        def is_available() -> bool:
            return False


dummy_torch = DummyTorch("torch")
dummy_torch.__spec__ = importlib.machinery.ModuleSpec(
    "torch", importlib.machinery.BuiltinImporter
)
sys.modules.setdefault("torch", dummy_torch)
import run_local


def test_parse_args():
    args = run_local.parse_args(['--model', 'foo', '--quant', '4', '--port', '1234'])
    assert args.model == 'foo'
    assert args.quant == 4
    assert args.port == 1234


def test_create_app(monkeypatch):
    class DummyTokenizer:
        def __call__(self, prompt, return_tensors=None):
            return types.SimpleNamespace(to=lambda x: {'input_ids': [0]})

        def decode(self, tokens, skip_special_tokens=True):
            return 'ok'

    class DummyModel:
        def to(self, device):
            return self

        def generate(self, **kwargs):
            return [[0]]

    monkeypatch.setattr(run_local, 'AutoTokenizer', types.SimpleNamespace(from_pretrained=lambda *a, **k: DummyTokenizer()))
    monkeypatch.setattr(run_local, 'AutoModelForCausalLM', types.SimpleNamespace(from_pretrained=lambda *a, **k: DummyModel()))
    monkeypatch.setattr(run_local.torch, 'cuda', types.SimpleNamespace(is_available=lambda: False))
    app = run_local.create_app('foo', None)
    assert isinstance(app, FastAPI)

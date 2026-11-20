# PR-Agent CLI with one patch: tiktoken's vocabulary download is blocked here,
# so token counts are approximated as ceil(bytes/4). Only matters near the
# context limit; the three fixtures are far below it.
import sys
from pr_agent.algo import token_handler
class ApproxEncoder:
    def encode(self, text, *a, **k): return [0] * (len(text.encode()) // 4 + 1)
token_handler.TokenEncoder._create_encoder = classmethod(lambda cls, model: ApproxEncoder())
from pr_agent.cli import run
sys.argv[0] = 'pr-agent'
run()

from logging import getLogger, Logger
from typing import Callable

from langchain.memory import ConversationBufferWindowMemory
from langchain.llms import OpenAI


class LLMAgent:

    def __init__(
        self,
        llm: OpenAI,
        memory=ConversationBufferWindowMemory(k=5),
        logger: Logger = getLogger(__name__),
    ):
        self.llm = llm
        self.memory = memory
        self.logger = logger

    def interact(
        self,
        pairs_of_header_body: list[tuple[str, str]],
        callback: Callable[[str], str] | None = None,
    ) -> str:

        # preparation
        if callback is None:
            def callback(x): return x

        # create input
        x = '\n\n,'.join([
            f'{header}\n{body}'
            for header, body in pairs_of_header_body
        ])

        # correct
        self.logger.info(f'input to llm: {x}')
        result = self.llm.predict(x)
        self.logger.info(f'output from llm: {result}')

        return callback(result)

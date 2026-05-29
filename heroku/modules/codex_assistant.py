import asyncio
import json
import logging
import time

from herokutl.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class CodexAssistant(loader.Module):
    """🤖 Codex AI Assistant"""

    strings = {"name": "CodexAI"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                None,
                lambda: "OpenAI API key (sk-...)",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "model",
                "gpt-4o-mini",
                lambda: "AI model",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "system_prompt",
                "You are Codex AI, an assistant in Heroku Userbot. "
                "Help with Python, Linux, Telegram. Be concise.",
                lambda: "System prompt",
            ),
        )

    async def _ask_openai(self, messages):
        import requests

        r = await utils.run_sync(
            requests.post,
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.config["model"],
                "messages": messages,
                "max_tokens": 2000,
            },
            timeout=60,
        )
        return r.json()

    @loader.command()
    async def codex(self, message: Message):
        """<question> | Ask Codex AI"""
        if not self.config["api_key"]:
            await utils.answer(
                message,
                "<b>❌ API key not set.</b>\n"
                f"Set: <code>{self.get_prefix()}cfg CodexAI api_key sk-...</code>"
            )
            return

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Usage:</b> <code>.codex &lt;question&gt;</code>")
            return

        msg = await utils.answer(message, "<b>🤖 Thinking...</b>")
        try:
            data = await self._ask_openai([
                {"role": "system", "content": self.config["system_prompt"]},
                {"role": "user", "content": args},
            ])

            if "error" in data:
                raise Exception(data["error"]["message"])

            reply = data["choices"][0]["message"]["content"].strip()
            await utils.answer(msg, f"<b>🤖 Codex:</b>\n{reply}")
        except Exception as e:
            await utils.answer(msg, f"<b>❌ Error:</b> <code>{utils.escape_html(str(e))}</code>")

    @loader.command()
    async def codexx(self, message: Message):
        """<code> | Explain code"""
        if not self.config["api_key"]:
            return

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Send code to explain</b>")
            return

        msg = await utils.answer(message, "<b>🔍 Analyzing...</b>")
        try:
            data = await self._ask_openai([
                {"role": "system", "content": "Explain this code briefly"},
                {"role": "user", "content": f"Explain:\n```\n{args}\n```"},
            ])

            if "error" in data:
                raise Exception(data["error"]["message"])

            await utils.answer(
                msg,
                f"<b>📝 Analysis:</b>\n{data['choices'][0]['message']['content'].strip()}"
            )
        except Exception as e:
            await utils.answer(msg, f"<b>❌ Error:</b> <code>{utils.escape_html(str(e))}</code>")

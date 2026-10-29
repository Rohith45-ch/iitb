#!/usr/bin/env python3
"""Minimal Gemini terminal chat client for this repository."""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def generate_reply(api_key: str, model: str, prompt: str) -> str:
    payload = json.dumps(
        {"contents": [{"parts": [{"text": prompt}]}]}
    ).encode("utf-8")
    request = Request(
        API_URL.format(model=model),
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    with urlopen(request, timeout=60) as response:
        result = json.load(response)

    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError("Gemini returned an unexpected response") from error


def main() -> int:
    parser = argparse.ArgumentParser(description="Chat with Gemini from the terminal")
    parser.add_argument("prompt", nargs="?", help="One prompt; omit for interactive chat")
    parser.add_argument("--model", default="gemini-3.8-flash", help="Gemini model name")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Set GEMINI_API_KEY in the terminal before starting chat.", file=sys.stderr)
        return 2

    if args.prompt:
        try:
            print(generate_reply(api_key, args.model, args.prompt))
        except (HTTPError, URLError, TimeoutError, OSError, RuntimeError) as error:
            print(f"Gemini request failed: {error}", file=sys.stderr)
            return 1
        return 0

    print("Gemini chat. Type /exit to quit.")
    while True:
        try:
            prompt = input("you> ").strip()
        except EOFError:
            break
        if prompt == "/exit":
            break
        if prompt:
            try:
                print(f"gemini> {generate_reply(api_key, args.model, prompt)}")
            except (HTTPError, URLError, TimeoutError, OSError, RuntimeError) as error:
                print(f"Gemini request failed: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
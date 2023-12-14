import time

from flask import Flask

app = Flask(__name__)


@app.route("/execute-tests")
def execute_tests():
    # Block: OpenAI
    # 1: Prompt Mode
    # 2: Knowledge Mode
    # 3: Search Mode

    # 4: Block: Perplexity
    # 5: Prompt Mode
    # 6: Knowledge Mode
    # 7: Search Mode

    # 8: Block: Qualification

    # 9: Block: Deepl

    # 10: Block: Database mode
    # 11: Block: Prepare Messages
    # 12: Block: AmoCRM

    return [
        {
            "block": "openai",
            "service": "prompt-mode",
            "success": True,
            "speed": time.time(),
        }
    ]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

import logging

from app.ai.ollama_provider import OllamaProvider
from app.config import load_settings
from app.logging_config import setup_logging
from app.memory import ConversationMemory


def main():
    settings = load_settings()
    setup_logging()
    logger = logging.getLogger("jarvis")

    memory = ConversationMemory(max_messages=settings.memory_limit)
    jarvis = OllamaProvider(
        model=settings.ollama_model,
        memory=memory,
    )

    print(f"\n=== {settings.app_name} ===")
    print(f"AI model: {settings.ollama_model}")
    print("Type /help for commands, or exit to quit.\n")
    logger.info("JARVIS-X chat started")

    while True:
        try:
            message = input("You: ").strip()

            if not message:
                continue

            command = message.lower()

            if command in {"exit", "quit"}:
                print("JARVIS: Bye Batman!")
                logger.info("JARVIS-X chat closed by user")
                break

            if command == "/help":
                print("\nCommands:")
                print("  /help    - Show commands")
                print("  /history - Show conversation history")
                print("  /clear   - Clear saved conversation history")
                print("  exit     - Quit JARVIS-X\n")
                continue

            if command == "/history":
                history = memory.get_messages()
                if not history:
                    print("\nJARVIS: No conversation history yet.\n")
                else:
                    print("\n--- Conversation History ---")
                    for item in history:
                        print(f'{item["role"].upper()}: {item["content"]}')
                    print()
                continue

            if command == "/clear":
                memory.clear()
                print("\nJARVIS: Conversation history cleared.\n")
                logger.info("Conversation memory cleared")
                continue

            logger.info("Processing user message")
            answer = jarvis.generate_response(message)
            print(f"\nJARVIS: {answer}\n")

        except (KeyboardInterrupt, EOFError):
            print("\nJARVIS: Chat closed.")
            logger.info("JARVIS-X chat interrupted")
            break
        except RuntimeError as error:
            logger.exception("AI provider error")
            print(f"\nJARVIS error: {error}")
            print("Check that Ollama is running, then restart JARVIS-X.")
            break
        except Exception:
            logger.exception("Unexpected chat error")
            print("\nJARVIS-X encountered an unexpected error.")
            print("Check logs/jarvis.log for details.")
            break


if __name__ == "__main__":
    main()

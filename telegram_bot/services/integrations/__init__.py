"""External integration providers package.

Import the registry-ready provider classes here.
The IntegrationManager (integration_manager.py) imports from this module.
"""
from telegram_bot.services.integrations.base import BaseIntegrationProvider, IntegrationConfig
from telegram_bot.services.integrations.youtube import YouTubeProvider
from telegram_bot.services.integrations.google_trends import GoogleTrendsProvider
from telegram_bot.services.integrations.openai_provider import OpenAIProvider
from telegram_bot.services.integrations.anthropic_provider import AnthropicProvider
from telegram_bot.services.integrations.openrouter import OpenRouterProvider
from telegram_bot.services.integrations.gemini import GeminiProvider

__all__ = [
    "BaseIntegrationProvider",
    "IntegrationConfig",
    "YouTubeProvider",
    "GoogleTrendsProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "OpenRouterProvider",
    "GeminiProvider",
]

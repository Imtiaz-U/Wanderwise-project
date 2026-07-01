"""
A couple of simple tests for Wanderwise.

Run with:  pytest test_wanderwise.py

We set a fake GROQ_API_KEY before importing the app, otherwise the app's
own startup check (sys.exit if no key is found) would stop these tests
from even running.
"""

import os
import builtins
from unittest.mock import patch, MagicMock

import httpx
import pytest

os.environ["GROQ_API_KEY"] = "test-key-not-real"

import backend_script as wanderwise
from groq import APIConnectionError, RateLimitError


# ---------- helpers ----------

def fake_inputs(values):
    """Lets us feed a list of fake 'typed' answers into input() one at a time."""
    values_iter = iter(values)
    return lambda prompt="": next(values_iter)


def make_fake_response(text):
    """Builds a fake Groq response object shaped like the real thing."""
    fake_message = MagicMock()
    fake_message.content = text
    fake_choice = MagicMock()
    fake_choice.message = fake_message
    fake_response = MagicMock()
    fake_response.choices = [fake_choice]
    return fake_response


# ---------- get_valid_budget ----------

def test_get_valid_budget_accepts_good_number(monkeypatch):
    monkeypatch.setattr(builtins, "input", fake_inputs(["500"]))
    assert wanderwise.get_valid_budget() == 500.0


def test_get_valid_budget_rejects_zero_then_accepts(monkeypatch, capsys):
    # First answer is 0 (invalid), second answer is a proper number
    monkeypatch.setattr(builtins, "input", fake_inputs(["0", "750"]))
    result = wanderwise.get_valid_budget()
    assert result == 750.0
    assert "greater than zero" in capsys.readouterr().out


def test_get_valid_budget_rejects_text_then_accepts(monkeypatch, capsys):
    # First answer is non-numeric (invalid), second is fine
    monkeypatch.setattr(builtins, "input", fake_inputs(["five", "200"]))
    result = wanderwise.get_valid_budget()
    assert result == 200.0
    assert "Invalid input" in capsys.readouterr().out


# ---------- get_required_text ----------

def test_get_required_text_accepts_normal_answer(monkeypatch):
    monkeypatch.setattr(builtins, "input", fake_inputs(["Tokyo"]))
    assert wanderwise.get_required_text("Where? ") == "Tokyo"


def test_get_required_text_rejects_empty_then_accepts(monkeypatch, capsys):
    # Empty string, then just spaces, then a real answer
    monkeypatch.setattr(builtins, "input", fake_inputs(["", "   ", "Paris"]))
    result = wanderwise.get_required_text("Where? ")
    assert result == "Paris"
    assert "can't be left empty" in capsys.readouterr().out


# ---------- generate_itinerary ----------

def test_generate_itinerary_returns_ai_text_on_success():
    fake_response = make_fake_response("Day 1: Visit the museum.")
    with patch.object(wanderwise.client.chat.completions, "create", return_value=fake_response):
        result = wanderwise.generate_itinerary("Tokyo", "5 days", 1000, "food", "budget")
    assert result == "Day 1: Visit the museum."


def test_generate_itinerary_handles_connection_error():
    fake_request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    connection_error = APIConnectionError(request=fake_request)

    with patch.object(wanderwise.client.chat.completions, "create", side_effect=connection_error):
        result = wanderwise.generate_itinerary("Tokyo", "5 days", 1000, "food", "budget")

    assert "couldn't connect" in result.lower()


def test_generate_itinerary_handles_rate_limit_error():
    fake_request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    fake_response = httpx.Response(429, request=fake_request)
    rate_limit_error = RateLimitError(message="Too many requests", response=fake_response, body=None)

    with patch.object(wanderwise.client.chat.completions, "create", side_effect=rate_limit_error):
        result = wanderwise.generate_itinerary("Tokyo", "5 days", 1000, "food", "budget")

    assert "rate limit" in result.lower()


def test_generate_itinerary_handles_empty_choices():
    fake_response = MagicMock()
    fake_response.choices = []

    with patch.object(wanderwise.client.chat.completions, "create", return_value=fake_response):
        result = wanderwise.generate_itinerary("Tokyo", "5 days", 1000, "food", "budget")

    assert "didn't send back any" in result.lower()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests

def querit_search(payload_data: dict) -> str:
    """
    Calls the Querit POST API to perform an advanced search.
    Reference: https://www.querit.ai/en/docs/reference/post
    """
    api_key = os.getenv("QUERIT_API_KEY")
    if not api_key:
        return json.dumps({"error": "QUERIT_API_KEY environment variable is missing. Please configure it in OpenClaw."})

    # Replace with the actual Querit POST endpoint URL
    url = "https://api.querit.ai/v1/search"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload_data, timeout=30)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)

    except requests.exceptions.RequestException as e:
        error_msg = f"Querit API request failed: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" | Response details: {e.response.text}"
        return json.dumps({"error": error_msg})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing input. Usage: python search.py '<json_string_or_query>'"}))
        sys.exit(1)

    raw_input = " ".join(sys.argv[1:])

    # Attempt to parse the input as a JSON payload for advanced queries
    try:
        payload = json.loads(raw_input)
        # Ensure 'query' exists if it was parsed as a dictionary
        if isinstance(payload, dict) and "query" not in payload:
            payload = {"query": str(payload)}
        elif not isinstance(payload, dict):
            payload = {"query": str(payload)}
    except json.JSONDecodeError:
        # Fallback: if it's not valid JSON, treat the entire string as a simple query
        payload = {"query": raw_input}

    # Execute the search and print the result
    result = querit_search(payload)
    print(result)
